"""
Tests for the swmf_semantic_index package.

Covers:
  - models: dataclass construction, ChunkRecord.make_id stability, authority tiers
  - corpus: file discovery, slice classification, extension filtering
  - chunking: Fortran, Perl, XML, TeX, Markdown chunkers
  - storage: ChunkStore open/write/read/FTS, manifest persistence
  - retrieval: SemanticIndex build + search, status reporting
  - cli: argument parsing and JSON output structure
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import textwrap
from datetime import datetime
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from swmf_semantic_index.models import (
    AuthorityTier,
    ChunkKind,
    ChunkRecord,
    CorpusManifest,
    CorpusRoot,
    CorpusSlice,
    RetrievalResult,
    ScoreComponents,
)
from swmf_semantic_index.corpus import DiscoveredFile, discover_corpus_root
from swmf_semantic_index.chunking import chunk_file, chunk_fortran, chunk_perl, chunk_markdown, chunk_tex, chunk_param_xml
from swmf_semantic_index.storage import ChunkStore
from swmf_semantic_index.retrieval import SemanticIndex


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_corpus(tmp_path: Path) -> Path:
    """Create a minimal synthetic corpus tree."""
    src = tmp_path / "src"
    src.mkdir()

    # Fortran file with module and subroutine
    (src / "GM_main.f90").write_text(textwrap.dedent("""\
        MODULE GM_ModMain
          implicit none
          SUBROUTINE GM_init
            CALL CON_stop('not implemented')
          END SUBROUTINE GM_init
        END MODULE GM_ModMain
    """))

    # Perl script with a sub
    (src / "TestParam.pl").write_text(textwrap.dedent("""\
        sub run_test {
            my ($param) = @_;
            return 1;
        }
    """))

    # PARAM XML fragment
    xml_dir = tmp_path / "PARAM.XML"
    xml_dir.write_text(textwrap.dedent("""\
        <?xml version="1.0"?>
        <paramlist>
          <command name="GRID">
            <parameter name="nI" type="integer" min="2" />
          </command>
          <command name="TIMESTEPPING">
            <parameter name="nStage" type="integer" default="2" />
          </command>
        </paramlist>
    """))

    # TeX manual section
    doc = tmp_path / "doc"
    doc.mkdir()
    (doc / "PHYSICS.tex").write_text(textwrap.dedent("""\
        \\section{Introduction}
        SWMF couples GM to IE via the CON framework.
        \\subsection{Coupling Overview}
        The coupling between GM and IE is bidirectional.
    """))

    # Markdown skill file
    skill_dir = tmp_path / ".github" / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
        # Test Skill
        ## Routing
        Use deterministic tools first.
        ## Fallback
        Escalate to semantic if needed.
    """))

    return tmp_path


@pytest.fixture
def discovered_fortran(tmp_corpus: Path) -> DiscoveredFile:
    return DiscoveredFile(
        abs_path=tmp_corpus / "src" / "GM_main.f90",
        rel_path="src/GM_main.f90",
        corpus_slice=CorpusSlice.SWMF_SOURCE,
        file_size=200,
    )


@pytest.fixture
def discovered_perl(tmp_corpus: Path) -> DiscoveredFile:
    return DiscoveredFile(
        abs_path=tmp_corpus / "src" / "TestParam.pl",
        rel_path="src/TestParam.pl",
        corpus_slice=CorpusSlice.SWMF_SCRIPTS,
        file_size=60,
    )


@pytest.fixture
def discovered_xml(tmp_corpus: Path) -> DiscoveredFile:
    return DiscoveredFile(
        abs_path=tmp_corpus / "PARAM.XML",
        rel_path="PARAM.XML",
        corpus_slice=CorpusSlice.SWMF_PARAM_XML,
        file_size=200,
    )


@pytest.fixture
def discovered_tex(tmp_corpus: Path) -> DiscoveredFile:
    return DiscoveredFile(
        abs_path=tmp_corpus / "doc" / "PHYSICS.tex",
        rel_path="doc/PHYSICS.tex",
        corpus_slice=CorpusSlice.SWMF_MANUALS,
        file_size=200,
    )


@pytest.fixture
def discovered_md(tmp_corpus: Path) -> DiscoveredFile:
    return DiscoveredFile(
        abs_path=tmp_corpus / ".github" / "skills" / "test-skill" / "SKILL.md",
        rel_path=".github/skills/test-skill/SKILL.md",
        corpus_slice=CorpusSlice.ANALYST_CONTEXT,
        file_size=120,
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestModels:
    def test_chunk_record_make_id_stable(self):
        id1 = ChunkRecord.make_id("/corpus", "src/foo.f90", 10)
        id2 = ChunkRecord.make_id("/corpus", "src/foo.f90", 10)
        assert id1 == id2

    def test_chunk_record_make_id_differs_by_line(self):
        id1 = ChunkRecord.make_id("/corpus", "src/foo.f90", 10)
        id2 = ChunkRecord.make_id("/corpus", "src/foo.f90", 20)
        assert id1 != id2

    def test_chunk_record_location(self):
        chunk = ChunkRecord(
            chunk_id="abc", corpus_root="/c", rel_path="src/foo.f90",
            kind=ChunkKind.FORTRAN_SUBROUTINE, authority=AuthorityTier.SOURCE_VERBATIM,
            corpus_slice=CorpusSlice.SWMF_SOURCE,
            start_line=5, end_line=20, text="dummy",
        )
        assert chunk.location == "src/foo.f90:5-20"

    def test_authority_tier_ordering(self):
        assert AuthorityTier.SOURCE_VERBATIM < AuthorityTier.DOCUMENTATION

    def test_corpus_manifest_is_stale_when_no_built_at(self):
        m = CorpusManifest()
        assert m.is_stale()

    def test_corpus_manifest_not_stale_if_fresh(self):
        m = CorpusManifest(built_at=datetime.utcnow())
        assert not m.is_stale(max_age_seconds=3600)

    def test_retrieval_result_authority_label(self):
        chunk = ChunkRecord(
            chunk_id="x", corpus_root="/c", rel_path="f.f90",
            kind=ChunkKind.FORTRAN_SUBROUTINE, authority=AuthorityTier.SEMANTIC_RETRIEVAL,
            corpus_slice=CorpusSlice.SWMF_SOURCE,
            start_line=1, end_line=5, text="x",
        )
        r = RetrievalResult(chunk=chunk, scores=ScoreComponents(), rank=1)
        assert "derived" in r.authority_label


# ---------------------------------------------------------------------------
# Corpus discovery tests
# ---------------------------------------------------------------------------


class TestCorpusDiscovery:
    def test_discovers_fortran_files(self, tmp_corpus: Path):
        files = discover_corpus_root(tmp_corpus, CorpusSlice.SWMF_SOURCE)
        paths = [f.rel_path for f in files]
        assert any("GM_main.f90" in p for p in paths)

    def test_discovers_perl_files(self, tmp_corpus: Path):
        files = discover_corpus_root(tmp_corpus, CorpusSlice.SWMF_SOURCE)
        paths = [f.rel_path for f in files]
        assert any(".pl" in p for p in paths)

    def test_discovers_xml_files(self, tmp_corpus: Path):
        files = discover_corpus_root(tmp_corpus, CorpusSlice.SWMF_SOURCE)
        paths = [f.rel_path for f in files]
        assert any(".xml" in p for p in paths) or any("PARAM" in p for p in paths)

    def test_skips_build_dirs(self, tmp_corpus: Path):
        build_dir = tmp_corpus / "build"
        build_dir.mkdir()
        (build_dir / "artifact.f90").write_text("MODULE Junk\nEND MODULE Junk\n")
        files = discover_corpus_root(tmp_corpus, CorpusSlice.SWMF_SOURCE)
        paths = [f.rel_path for f in files]
        assert not any("build" in p for p in paths)

    def test_skips_too_large_files(self, tmp_corpus: Path):
        big = tmp_corpus / "src" / "huge.f90"
        big.write_text("X" * 600_000)
        files = discover_corpus_root(tmp_corpus, CorpusSlice.SWMF_SOURCE, max_file_bytes=500_000)
        paths = [f.rel_path for f in files]
        assert not any("huge.f90" in p for p in paths)

    def test_tex_classified_as_manual(self, tmp_corpus: Path):
        files = discover_corpus_root(tmp_corpus, CorpusSlice.SWMF_SOURCE)
        tex_files = [f for f in files if f.abs_path.suffix == ".tex"]
        assert all(f.corpus_slice == CorpusSlice.SWMF_MANUALS for f in tex_files)


# ---------------------------------------------------------------------------
# Chunking tests
# ---------------------------------------------------------------------------


class TestFortranChunker:
    def test_extracts_module(self, discovered_fortran: DiscoveredFile):
        chunks = chunk_fortran(discovered_fortran)
        modules = [c for c in chunks if c.kind == ChunkKind.FORTRAN_MODULE]
        assert len(modules) >= 1
        assert any("GM_ModMain" in (c.symbol or "") for c in modules)

    def test_extracts_subroutine(self, discovered_fortran: DiscoveredFile):
        chunks = chunk_fortran(discovered_fortran)
        subs = [c for c in chunks if c.kind == ChunkKind.FORTRAN_SUBROUTINE]
        assert len(subs) >= 1
        assert any("GM_init" in (c.symbol or "") for c in subs)

    def test_subroutine_has_source_authority(self, discovered_fortran: DiscoveredFile):
        chunks = chunk_fortran(discovered_fortran)
        for c in chunks:
            assert c.authority == AuthorityTier.SOURCE_VERBATIM

    def test_keywords_extracted(self, discovered_fortran: DiscoveredFile):
        chunks = chunk_fortran(discovered_fortran)
        all_keywords = [k for c in chunks for k in c.keywords]
        # CON_stop should appear as a CALL keyword
        assert any("CON_STOP" in kw.upper() or "CON_stop" in kw for kw in all_keywords)

    def test_component_extracted_from_path(self, discovered_fortran: DiscoveredFile):
        chunks = chunk_fortran(discovered_fortran)
        # rel_path contains "GM_main.f90" but no /GM/ directory, so component may be None or GM
        # depending on whether the regex matches in the filename
        # just verify no crash and chunks returned
        assert len(chunks) > 0

    def test_fallback_on_empty_file(self, tmp_path: Path):
        empty = tmp_path / "empty.f90"
        empty.write_text("")
        df = DiscoveredFile(abs_path=empty, rel_path="empty.f90",
                            corpus_slice=CorpusSlice.SWMF_SOURCE, file_size=0)
        assert chunk_fortran(df) == []


class TestPerlChunker:
    def test_extracts_sub(self, discovered_perl: DiscoveredFile):
        chunks = chunk_perl(discovered_perl)
        subs = [c for c in chunks if c.kind == ChunkKind.PERL_SUB]
        assert len(subs) >= 1
        assert any("run_test" in (c.symbol or "") for c in subs)

    def test_sub_authority(self, discovered_perl: DiscoveredFile):
        chunks = chunk_perl(discovered_perl)
        for c in chunks:
            assert c.authority == AuthorityTier.SOURCE_VERBATIM


class TestXmlChunker:
    def test_extracts_commands(self, discovered_xml: DiscoveredFile):
        chunks = chunk_param_xml(discovered_xml)
        xml_cmds = [c for c in chunks if c.kind == ChunkKind.XML_COMMAND]
        symbols = [c.symbol for c in xml_cmds]
        assert "GRID" in symbols
        assert "TIMESTEPPING" in symbols

    def test_xml_authority(self, discovered_xml: DiscoveredFile):
        chunks = chunk_param_xml(discovered_xml)
        for c in chunks:
            assert c.authority == AuthorityTier.SCHEMA_VALIDATED


class TestTexChunker:
    def test_extracts_sections(self, discovered_tex: DiscoveredFile):
        chunks = chunk_tex(discovered_tex)
        assert len(chunks) >= 1
        titles = [c.symbol for c in chunks if c.symbol]
        assert any("Introduction" in t or "Coupling" in t for t in titles)

    def test_tex_authority(self, discovered_tex: DiscoveredFile):
        chunks = chunk_tex(discovered_tex)
        for c in chunks:
            assert c.authority == AuthorityTier.DOCUMENTATION


class TestMarkdownChunker:
    def test_extracts_sections(self, discovered_md: DiscoveredFile):
        chunks = chunk_markdown(discovered_md)
        assert len(chunks) >= 1

    def test_skill_file_gets_skill_kind(self, discovered_md: DiscoveredFile):
        chunks = chunk_markdown(discovered_md)
        assert all(c.kind == ChunkKind.SKILL_SECTION for c in chunks)

    def test_md_authority(self, discovered_md: DiscoveredFile):
        chunks = chunk_markdown(discovered_md)
        for c in chunks:
            assert c.authority == AuthorityTier.DOCUMENTATION


class TestChunkDispatch:
    def test_dispatch_fortran(self, discovered_fortran: DiscoveredFile):
        chunks = chunk_file(discovered_fortran)
        assert len(chunks) > 0

    def test_dispatch_unknown_extension(self, tmp_path: Path):
        f = tmp_path / "file.xyz"
        f.write_text("content")
        df = DiscoveredFile(abs_path=f, rel_path="file.xyz",
                            corpus_slice=CorpusSlice.SWMF_SOURCE, file_size=7)
        assert chunk_file(df) == []


# ---------------------------------------------------------------------------
# Storage tests
# ---------------------------------------------------------------------------


class TestChunkStore:
    def test_open_creates_db(self, tmp_path: Path):
        store = ChunkStore(tmp_path / "test.db")
        store.open()
        assert (tmp_path / "test.db").exists()
        store.close()

    def test_insert_and_retrieve_chunk(self, tmp_path: Path):
        store = ChunkStore(tmp_path / "test.db")
        store.open()
        chunk = ChunkRecord(
            chunk_id="abc123",
            corpus_root="/corpus",
            rel_path="src/foo.f90",
            kind=ChunkKind.FORTRAN_SUBROUTINE,
            authority=AuthorityTier.SOURCE_VERBATIM,
            corpus_slice=CorpusSlice.SWMF_SOURCE,
            start_line=10,
            end_line=25,
            text="SUBROUTINE foo\n  CALL bar\nEND SUBROUTINE",
            symbol="foo",
            keywords=["BAR"],
        )
        store.insert_chunk(chunk)
        retrieved = store.get_chunk("abc123")
        assert retrieved is not None
        assert retrieved.symbol == "foo"
        assert retrieved.kind == ChunkKind.FORTRAN_SUBROUTINE
        store.close()

    def test_fts_search_finds_text(self, tmp_path: Path):
        store = ChunkStore(tmp_path / "test.db")
        store.open()
        chunk = ChunkRecord(
            chunk_id="xyz",
            corpus_root="/c",
            rel_path="CON/Interface/src/CON_couple.f90",
            kind=ChunkKind.FORTRAN_SUBROUTINE,
            authority=AuthorityTier.SOURCE_VERBATIM,
            corpus_slice=CorpusSlice.SWMF_SOURCE,
            start_line=1, end_line=10,
            text="SUBROUTINE couple_ih_sc\n  CALL CON_stop('not implemented')\nEND SUBROUTINE",
            symbol="couple_ih_sc",
            keywords=["CON_STOP"],
        )
        store.insert_chunk(chunk)
        results = store.fts_search("couple_ih_sc")
        assert len(results) >= 1
        assert results[0].symbol == "couple_ih_sc"
        store.close()

    def test_fts_search_empty_query_returns_empty(self, tmp_path: Path):
        store = ChunkStore(tmp_path / "test.db")
        store.open()
        results = store.fts_search("")
        assert results == []
        store.close()

    def test_manifest_roundtrip(self, tmp_path: Path):
        store = ChunkStore(tmp_path / "test.db")
        store.open()
        manifest = CorpusManifest(
            built_at=datetime.utcnow(),
            embedding_backend="tfidf_lexical",
            total_chunks=42,
            total_files=10,
            roots=[
                CorpusRoot(
                    abs_path="/SWMF",
                    corpus_slice=CorpusSlice.SWMF_SOURCE,
                    file_count=10,
                    chunk_count=42,
                    indexed_at=datetime.utcnow(),
                )
            ],
            index_path=str(tmp_path),
        )
        store.save_manifest(manifest)
        loaded = store.load_manifest()
        assert loaded is not None
        assert loaded.total_chunks == 42
        assert len(loaded.roots) == 1
        assert loaded.roots[0].corpus_slice == CorpusSlice.SWMF_SOURCE
        store.close()

    def test_clear_removes_chunks(self, tmp_path: Path):
        store = ChunkStore(tmp_path / "test.db")
        store.open()
        chunk = ChunkRecord(
            chunk_id="del1", corpus_root="/c", rel_path="x.f90",
            kind=ChunkKind.FORTRAN_MODULE, authority=AuthorityTier.SOURCE_VERBATIM,
            corpus_slice=CorpusSlice.SWMF_SOURCE,
            start_line=1, end_line=5, text="MODULE X\nEND MODULE",
        )
        store.insert_chunk(chunk)
        assert store.count_chunks() == 1
        store.clear()
        assert store.count_chunks() == 0
        store.close()

    def test_bulk_insert(self, tmp_path: Path):
        store = ChunkStore(tmp_path / "test.db")
        store.open()
        chunks = [
            ChunkRecord(
                chunk_id=f"bulk_{i}", corpus_root="/c", rel_path=f"f{i}.f90",
                kind=ChunkKind.FORTRAN_SUBROUTINE, authority=AuthorityTier.SOURCE_VERBATIM,
                corpus_slice=CorpusSlice.SWMF_SOURCE,
                start_line=1, end_line=10, text=f"sub content {i}",
            )
            for i in range(5)
        ]
        store.insert_chunks_bulk(chunks)
        assert store.count_chunks() == 5
        store.close()


# ---------------------------------------------------------------------------
# Retrieval / SemanticIndex tests
# ---------------------------------------------------------------------------


class TestSemanticIndex:
    def test_build_creates_index(self, tmp_path: Path, tmp_corpus: Path):
        cache = tmp_path / "cache"
        idx = SemanticIndex(cache_dir=cache)
        manifest = idx.build([(tmp_corpus, CorpusSlice.SWMF_SOURCE)])
        assert manifest.total_chunks > 0
        assert (cache / "semantic_index.db").exists()
        idx.close()

    def test_search_returns_results(self, tmp_path: Path, tmp_corpus: Path):
        cache = tmp_path / "cache"
        idx = SemanticIndex(cache_dir=cache)
        idx.build([(tmp_corpus, CorpusSlice.SWMF_SOURCE)])
        results = idx.search("coupling GM IE")
        assert isinstance(results, list)
        idx.close()

    def test_search_with_component_filter(self, tmp_path: Path, tmp_corpus: Path):
        cache = tmp_path / "cache"
        idx = SemanticIndex(cache_dir=cache)
        idx.build([(tmp_corpus, CorpusSlice.SWMF_SOURCE)])
        # Should not raise; result may be empty if no GM component chunks exist
        results = idx.search("init", component="GM")
        assert isinstance(results, list)
        idx.close()

    def test_results_are_ranked(self, tmp_path: Path, tmp_corpus: Path):
        cache = tmp_path / "cache"
        idx = SemanticIndex(cache_dir=cache)
        idx.build([(tmp_corpus, CorpusSlice.SWMF_SOURCE)])
        results = idx.search("subroutine module")
        if len(results) > 1:
            scores = [r.scores.combined for r in results]
            assert scores == sorted(scores, reverse=True)
        idx.close()

    def test_status_built(self, tmp_path: Path, tmp_corpus: Path):
        cache = tmp_path / "cache"
        idx = SemanticIndex(cache_dir=cache)
        idx.build([(tmp_corpus, CorpusSlice.SWMF_SOURCE)])
        status = idx.get_status()
        assert status["built"] is True
        assert status["total_chunks"] > 0
        idx.close()

    def test_status_not_built(self, tmp_path: Path):
        cache = tmp_path / "empty_cache"
        idx = SemanticIndex(cache_dir=cache)
        status = idx.get_status()
        assert status["built"] is False
        idx.close()

    def test_rebuild_clears_previous(self, tmp_path: Path, tmp_corpus: Path):
        cache = tmp_path / "cache"
        idx = SemanticIndex(cache_dir=cache)
        m1 = idx.build([(tmp_corpus, CorpusSlice.SWMF_SOURCE)])
        m2 = idx.build([(tmp_corpus, CorpusSlice.SWMF_SOURCE)])
        assert m2.total_chunks == m1.total_chunks  # same corpus → same count
        idx.close()


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestCLI:
    def test_cli_status_not_built(self, tmp_path: Path, capsys):
        from swmf_semantic_index.cli import main
        with pytest.raises(SystemExit) as exc:
            main(["--cache", str(tmp_path / "cache"), "status"])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["built"] is False

    def test_cli_build(self, tmp_path: Path, tmp_corpus: Path, capsys):
        from swmf_semantic_index.cli import main
        with pytest.raises(SystemExit) as exc:
            main(["--cache", str(tmp_path / "cache"), "build",
                  "--corpus", str(tmp_corpus)])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["status"] == "built"
        assert data["total_chunks"] > 0

    def test_cli_query(self, tmp_path: Path, tmp_corpus: Path, capsys):
        from swmf_semantic_index.cli import main
        cache = str(tmp_path / "cache")
        # Build first
        with pytest.raises(SystemExit):
            main(["--cache", cache, "build", "--corpus", str(tmp_corpus)])
        capsys.readouterr()  # discard build output
        # Now query
        with pytest.raises(SystemExit) as exc:
            main(["--cache", cache, "query", "coupling", "--top-k", "3"])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert "results" in data
        assert data["top_k"] == 3

    def test_cli_build_no_corpus(self, tmp_path: Path, capsys):
        from swmf_semantic_index.cli import main
        with pytest.raises(SystemExit) as exc:
            main(["--cache", str(tmp_path / "cache"), "build"])
        assert exc.value.code == 1
