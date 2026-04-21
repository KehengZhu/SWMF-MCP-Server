"""Architecture tests for the SWMF knowledge base.

Covers
------
* Fortran and Perl parser extraction from representative source snippets
* SourceIndexCatalog build, status, search, lookup, and param evidence
* Incremental refresh (new / changed / deleted files)
* KnowledgeService retrieval API
* MCP tool response shapes (refresh, search, lookup, evidence, status)
* MCP resource response shapes
* PARAM schema resource additive source_evidence field
* swmf_explain_param additive source_evidence field
* Authority discipline: knowledge results never override authoritative PARAM.XML
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from swmf_mcp_server.parsing.fortran_parser import FortranSymbol, parse_fortran_file
from swmf_mcp_server.parsing.perl_parser import PerlSymbol, parse_perl_file
from swmf_mcp_server.catalog.source_index_catalog import SourceIndexCatalog
from swmf_mcp_server.core import knowledge_service as ks
from swmf_mcp_server.core.authority import (
    AUTHORITY_HEURISTIC,
    SOURCE_KIND_FORTRAN_SOURCE,
    SOURCE_KIND_PERL_SOURCE,
)
from swmf_mcp_server.core.models import KnowledgeIndexStatus


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


FORTRAN_SAMPLE = """\
! Read all parameters for this session
subroutine ReadParam(NameCommand)
  use ModReadParam, ONLY: read_var, read_line
  use ModMain,      ONLY: nStep
  ! Main dispatch loop
  select case(NameCommand)
  case('#STOP')
    call read_var('MaxIteration', MaxIteration)
  case('#TIMEACCURATE')
    call read_var('DoTimeAccurate', DoTimeAccurate)
  end select
end subroutine ReadParam

! Module for global state
module ModGlobal
  implicit none
  integer :: nStep = 0
end module ModGlobal

! Compute CFL timestep
real function CalcTimestep(iCell)
  use ModPhysics
  CalcTimestep = dx / maxval(speed)
end function CalcTimestep
"""

PERL_SAMPLE = """\
# Validate the PARAM.in file structure
sub ValidateParam {
    my ($file, $nProc) = @_;
    if (is_command($file, '#STOP')) {
        CheckStop($file);
    }
}

# Apply '#MAGNETOGRAM' block settings
sub ApplyMagnetogram {
    my ($param) = @_;
    process_magnetogram($param, '#MAGNETOGRAM');
}

sub _helper {
    # internal helper
}
"""


@pytest.fixture()
def fake_swmf_root(tmp_path: Path) -> Path:
    """A minimal fake SWMF root with source files for indexing."""
    root = tmp_path / "SWMF"

    # SWMF root markers
    (root / "Scripts").mkdir(parents=True)
    (root / "Config.pl").write_text("#!/usr/bin/env perl\nsub Configure { }\n", encoding="utf-8")
    (root / "Scripts" / "TestParam.pl").write_text(
        "#!/usr/bin/env perl\n# Validate '#STOP' and '#TIMEACCURATE'\nsub TestParam { }\n",
        encoding="utf-8",
    )
    (root / "PARAM.XML").write_text(
        "<commandList>\n"
        '  <command name="#STOP" type="real" default="3600.0" min="0" max="100000">\n'
        "  Stop criteria.\n  </command>\n"
        "</commandList>\n",
        encoding="utf-8",
    )

    # Fortran control layer
    src = root / "src"
    src.mkdir()
    (src / "CON_session.f90").write_text(FORTRAN_SAMPLE, encoding="utf-8")

    # Perl script
    (root / "Scripts" / "Restart.pl").write_text(PERL_SAMPLE + "\n\nsub _helper {\n    # internal helper\n}\n", encoding="utf-8")

    # Component source
    gm_src = root / "GM" / "BATSRUS" / "src"
    gm_src.mkdir(parents=True)
    (gm_src / "ModMain.f90").write_text(
        "! Main module\nmodule ModMain\n  integer :: nStep\nend module ModMain\n",
        encoding="utf-8",
    )
    (gm_src / "PARAM.XML").write_text(
        "<commandList>\n"
        '  <command name="#TIMESTEP" type="real" default="0.5" />\n'
        "</commandList>\n",
        encoding="utf-8",
    )

    return root


# ---------------------------------------------------------------------------
# Fortran parser
# ---------------------------------------------------------------------------


class TestFortranParser:
    def test_extracts_subroutine(self) -> None:
        symbols = parse_fortran_file("dummy.f90", text=FORTRAN_SAMPLE)
        names = [s.name for s in symbols]
        assert "ReadParam" in names

    def test_extracts_module(self) -> None:
        symbols = parse_fortran_file("dummy.f90", text=FORTRAN_SAMPLE)
        mods = [s for s in symbols if s.kind == "module"]
        assert any(s.name == "ModGlobal" for s in mods)

    def test_extracts_function(self) -> None:
        symbols = parse_fortran_file("dummy.f90", text=FORTRAN_SAMPLE)
        funs = [s for s in symbols if s.kind == "function"]
        assert any(s.name == "CalcTimestep" for s in funs)

    def test_docstring_collected_above_declaration(self) -> None:
        symbols = parse_fortran_file("dummy.f90", text=FORTRAN_SAMPLE)
        read_param = next(s for s in symbols if s.name == "ReadParam")
        assert read_param.docstring is not None
        assert "Read all parameters" in read_param.docstring

    def test_param_refs_extracted_from_body(self) -> None:
        symbols = parse_fortran_file("dummy.f90", text=FORTRAN_SAMPLE)
        read_param = next(s for s in symbols if s.name == "ReadParam")
        assert "STOP" in read_param.param_refs
        assert "TIMEACCURATE" in read_param.param_refs

    def test_uses_collected(self) -> None:
        symbols = parse_fortran_file("dummy.f90", text=FORTRAN_SAMPLE)
        read_param = next(s for s in symbols if s.name == "ReadParam")
        assert "ModReadParam" in read_param.uses

    def test_start_line_is_one_based(self) -> None:
        symbols = parse_fortran_file("dummy.f90", text=FORTRAN_SAMPLE)
        read_param = next(s for s in symbols if s.name == "ReadParam")
        assert read_param.start_line >= 1

    def test_missing_file_returns_empty(self) -> None:
        assert parse_fortran_file("/nonexistent/path.f90") == []


# ---------------------------------------------------------------------------
# Perl parser
# ---------------------------------------------------------------------------


class TestPerlParser:
    def test_extracts_subs(self) -> None:
        symbols = parse_perl_file("dummy.pl", text=PERL_SAMPLE)
        names = [s.name for s in symbols]
        assert "ValidateParam" in names
        assert "ApplyMagnetogram" in names

    def test_docstring_collected(self) -> None:
        symbols = parse_perl_file("dummy.pl", text=PERL_SAMPLE)
        vp = next(s for s in symbols if s.name == "ValidateParam")
        assert vp.docstring is not None
        assert "Validate" in vp.docstring

    def test_param_refs_extracted(self) -> None:
        symbols = parse_perl_file("dummy.pl", text=PERL_SAMPLE)
        vp = next(s for s in symbols if s.name == "ValidateParam")
        assert "STOP" in vp.param_refs

        am = next(s for s in symbols if s.name == "ApplyMagnetogram")
        assert "MAGNETOGRAM" in am.param_refs

    def test_missing_file_returns_empty(self) -> None:
        assert parse_perl_file("/nonexistent/path.pl") == []


# ---------------------------------------------------------------------------
# SourceIndexCatalog
# ---------------------------------------------------------------------------


class TestSourceIndexCatalog:
    def test_status_not_built_before_build(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        status = catalog.get_status()
        assert status.is_stale is True
        assert status.ok is False

    def test_build_creates_index(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        status = catalog.build()
        assert status.ok is True
        assert status.is_stale is False
        assert status.symbol_count > 0
        assert status.file_count > 0

    def test_build_skips_when_fresh(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        s1 = catalog.build()
        s2 = catalog.build()  # should skip
        assert s2.ok is True
        assert s2.symbol_count == s1.symbol_count

    def test_build_force_rebuilds(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build()
        status = catalog.build(force=True)
        assert status.ok is True

    def test_search_symbols_finds_subroutine(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build()
        results = catalog.search_symbols("ReadParam")
        assert len(results) >= 1
        assert any(r["name"] == "ReadParam" for r in results)

    def test_search_symbols_component_filter(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build()
        # GM component has ModMain
        gm_results = catalog.search_symbols("ModMain", component="GM")
        assert any(r["name"] == "ModMain" for r in gm_results)

    def test_lookup_symbol_exact(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build()
        matches = catalog.lookup_symbol("ReadParam")
        assert len(matches) >= 1
        assert matches[0]["name"] == "ReadParam"

    def test_lookup_symbol_case_insensitive(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build()
        assert catalog.lookup_symbol("readparam")  # lowercase

    def test_get_param_evidence_finds_stop(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build()
        evidence = catalog.get_param_evidence("STOP")
        assert len(evidence) >= 1
        assert any(
            r.get("name") == "ReadParam" or "STOP" in r.get("file_path", "")
            for r in evidence
        )

    def test_get_param_evidence_all_heuristic(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build()
        evidence = catalog.get_param_evidence("STOP")
        for item in evidence:
            assert item.get("authority") == AUTHORITY_HEURISTIC

    def test_source_files_not_built_returns_empty(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        # No build — all query methods should return empty gracefully
        assert catalog.search_symbols("ReadParam") == []
        assert catalog.lookup_symbol("ReadParam") == []
        assert catalog.get_param_evidence("STOP") == []

    def test_refresh_indexes_new_file(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build()
        before = catalog.get_status().symbol_count

        # Add a new Fortran file
        new_file = fake_swmf_root / "src" / "NewModule.f90"
        new_file.write_text(
            "! New helper\nsubroutine NewHelper(x)\n  use ModMain\nend subroutine NewHelper\n",
            encoding="utf-8",
        )
        catalog.refresh()
        after = catalog.get_status().symbol_count
        assert after > before

    def test_refresh_removes_deleted_file(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build()

        # Add then delete a file
        extra = fake_swmf_root / "src" / "TempModule.f90"
        extra.write_text("subroutine TempSub()\nend subroutine TempSub\n", encoding="utf-8")
        catalog.refresh()
        assert catalog.lookup_symbol("TempSub")

        extra.unlink()
        catalog.refresh()
        assert not catalog.lookup_symbol("TempSub")

    def test_db_path_inside_swmf_root(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        assert str(fake_swmf_root) in catalog._db_path.parts or str(fake_swmf_root) in str(catalog._db_path)


# ---------------------------------------------------------------------------
# KnowledgeService (retrieval API)
# ---------------------------------------------------------------------------


class TestKnowledgeService:
    def test_get_index_status_before_build(self, fake_swmf_root: Path) -> None:
        status = ks.get_index_status(str(fake_swmf_root))
        assert status.is_stale is True

    def test_search_auto_builds_when_missing(self, fake_swmf_root: Path) -> None:
        results = ks.search_symbols(str(fake_swmf_root), query="ReadParam")
        assert any(r["name"] == "ReadParam" for r in results)

    def test_build_then_search(self, fake_swmf_root: Path) -> None:
        ks.build_index(str(fake_swmf_root), force=True)
        results = ks.search_symbols(str(fake_swmf_root), query="ReadParam")
        assert any(r["name"] == "ReadParam" for r in results)

    def test_get_param_evidence_via_service(self, fake_swmf_root: Path) -> None:
        ks.build_index(str(fake_swmf_root), force=True)
        evidence = ks.get_param_evidence(str(fake_swmf_root), command_normalized="STOP")
        assert len(evidence) >= 1

    def test_status_as_payload_shape(self, fake_swmf_root: Path) -> None:
        ks.build_index(str(fake_swmf_root), force=True)
        status = ks.get_index_status(str(fake_swmf_root))
        payload = ks.status_as_payload(status)
        for key in ("ok", "db_path", "swmf_root", "schema_version", "symbol_count", "file_count", "is_stale"):
            assert key in payload


# ---------------------------------------------------------------------------
# MCP tool shapes
# ---------------------------------------------------------------------------


class TestKnowledgeTools:
    def test_refresh_tool_builds_index(self, fake_swmf_root: Path) -> None:
        from swmf_mcp_server.tools.knowledge import swmf_refresh_knowledge_index

        result = swmf_refresh_knowledge_index(swmf_root=str(fake_swmf_root), force_rebuild=True)
        assert result["ok"] is True
        assert result["symbol_count"] > 0
        assert result["action"] == "force_rebuild"

    def test_search_tool_returns_results(self, fake_swmf_root: Path) -> None:
        from swmf_mcp_server.tools.knowledge import swmf_refresh_knowledge_index, swmf_search_source

        swmf_refresh_knowledge_index(swmf_root=str(fake_swmf_root), force_rebuild=True)
        result = swmf_search_source(query="ReadParam", swmf_root=str(fake_swmf_root))
        assert result["ok"] is True
        assert result["result_count"] >= 1
        assert result["authority"] == AUTHORITY_HEURISTIC

    def test_search_tool_auto_builds_without_index(self, fake_swmf_root: Path) -> None:
        from swmf_mcp_server.tools.knowledge import swmf_search_source

        result = swmf_search_source(query="ReadParam", swmf_root=str(fake_swmf_root))
        assert result["ok"] is True
        assert result["result_count"] >= 1

    def test_lookup_tool_auto_builds_without_index(self, fake_swmf_root: Path) -> None:
        from swmf_mcp_server.tools.knowledge import swmf_lookup_source_symbol

        result = swmf_lookup_source_symbol(name="ReadParam", swmf_root=str(fake_swmf_root))
        assert result["ok"] is True
        assert result["match_count"] >= 1

    def test_param_evidence_tool_auto_builds_without_index(self, fake_swmf_root: Path) -> None:
        from swmf_mcp_server.tools.knowledge import swmf_get_param_source_evidence

        result = swmf_get_param_source_evidence(command="#STOP", swmf_root=str(fake_swmf_root))
        assert result["ok"] is True
        assert result["evidence_count"] >= 1

    def test_lookup_tool_shape(self, fake_swmf_root: Path) -> None:
        from swmf_mcp_server.tools.knowledge import swmf_lookup_source_symbol, swmf_refresh_knowledge_index

        swmf_refresh_knowledge_index(swmf_root=str(fake_swmf_root), force_rebuild=True)
        result = swmf_lookup_source_symbol(name="ReadParam", swmf_root=str(fake_swmf_root))
        assert result["ok"] is True
        assert result["match_count"] >= 1
        assert all("file_path" in m for m in result["matches"])

    def test_param_evidence_tool_shape(self, fake_swmf_root: Path) -> None:
        from swmf_mcp_server.tools.knowledge import swmf_get_param_source_evidence, swmf_refresh_knowledge_index

        swmf_refresh_knowledge_index(swmf_root=str(fake_swmf_root), force_rebuild=True)
        result = swmf_get_param_source_evidence(command="#STOP", swmf_root=str(fake_swmf_root))
        assert result["ok"] is True
        assert result["command"] == "#STOP"
        assert result["command_normalized"] == "STOP"
        assert result["authority"] == AUTHORITY_HEURISTIC
        assert "note" in result

    def test_param_evidence_normalizes_hash_prefix(self, fake_swmf_root: Path) -> None:
        from swmf_mcp_server.tools.knowledge import swmf_get_param_source_evidence, swmf_refresh_knowledge_index

        swmf_refresh_knowledge_index(swmf_root=str(fake_swmf_root), force_rebuild=True)
        # Both "#STOP" and "STOP" should work
        r1 = swmf_get_param_source_evidence(command="#STOP", swmf_root=str(fake_swmf_root))
        r2 = swmf_get_param_source_evidence(command="STOP", swmf_root=str(fake_swmf_root))
        assert r1["command_normalized"] == r2["command_normalized"] == "STOP"

    def test_status_tool_shape(self, fake_swmf_root: Path) -> None:
        from swmf_mcp_server.tools.knowledge import swmf_get_knowledge_index_status, swmf_refresh_knowledge_index

        swmf_refresh_knowledge_index(swmf_root=str(fake_swmf_root), force_rebuild=True)
        result = swmf_get_knowledge_index_status(swmf_root=str(fake_swmf_root))
        assert result["ok"] is True
        assert result["is_stale"] is False
        assert "symbol_count" in result
        assert "file_count" in result


# ---------------------------------------------------------------------------
# MCP resource shapes
# ---------------------------------------------------------------------------


class TestKnowledgeResources:
    def test_symbol_resource_auto_builds(self, fake_swmf_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from swmf_mcp_server.resources import source_knowledge

        monkeypatch.setattr(source_knowledge, "_resolve_root", lambda: str(fake_swmf_root))

        result = source_knowledge.get_symbol_resource("ReadParam")
        assert result["ok"] is True
        assert result["match_count"] >= 1

    def test_symbol_resource_shape(self, fake_swmf_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from swmf_mcp_server.resources import source_knowledge
        from swmf_mcp_server.core import knowledge_service

        ks.build_index(str(fake_swmf_root), force=True)
        monkeypatch.setattr(source_knowledge, "_resolve_root", lambda: str(fake_swmf_root))

        result = source_knowledge.get_symbol_resource("ReadParam")
        assert result["ok"] is True
        assert result["match_count"] >= 1
        assert result["authority"] == AUTHORITY_HEURISTIC

    def test_index_status_resource_shape(self, fake_swmf_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from swmf_mcp_server.resources import source_knowledge

        ks.build_index(str(fake_swmf_root), force=True)
        monkeypatch.setattr(source_knowledge, "_resolve_root", lambda: str(fake_swmf_root))

        result = source_knowledge.get_index_status_resource()
        assert "symbol_count" in result
        assert "file_count" in result
        assert "is_stale" in result


# ---------------------------------------------------------------------------
# Authority discipline — knowledge results must not override authoritative
# ---------------------------------------------------------------------------


class TestAuthorityDiscipline:
    def test_explain_param_authority_preserved_with_catalog(self, fake_swmf_root: Path) -> None:
        """swmf_explain_param must remain authoritative when PARAM.XML is present."""
        from swmf_mcp_server import server

        ks.build_index(str(fake_swmf_root), force=True)
        result = server.swmf_explain_param(
            name="#STOP",
            swmf_root=str(fake_swmf_root),
            force_refresh=True,
        )
        assert result["found"] is True
        assert result["authority"] == "authoritative"  # not overridden by heuristic index

    def test_explain_param_source_evidence_is_additive(self, fake_swmf_root: Path) -> None:
        """source_evidence must be present but not affect the authority field."""
        from swmf_mcp_server import server

        ks.build_index(str(fake_swmf_root), force=True)
        result = server.swmf_explain_param(
            name="#STOP",
            swmf_root=str(fake_swmf_root),
            force_refresh=True,
        )
        # Field exists (even if empty)
        assert "source_evidence" in result
        assert "source_evidence_count" in result
        # authority unchanged
        assert result["authority"] == "authoritative"

    def test_source_evidence_is_all_heuristic(self, fake_swmf_root: Path) -> None:
        ks.build_index(str(fake_swmf_root), force=True)
        evidence = ks.get_param_evidence(str(fake_swmf_root), command_normalized="STOP")
        for item in evidence:
            assert item.get("authority") == AUTHORITY_HEURISTIC

    def test_param_schema_source_evidence_additive(self, fake_swmf_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """param_schema resource must expose source_evidence without changing existing fields."""
        from swmf_mcp_server.core.models import CommandMetadata, ComponentVersion, SourceCatalog
        from swmf_mcp_server.resources import param_schema

        ks.build_index(str(fake_swmf_root), force=True)

        stop_cmd = CommandMetadata(
            name="#STOP",
            normalized="STOP",
            component="CON",
            description="Stop criteria",
            source_kind="PARAM.XML",
            source_path=str(fake_swmf_root / "PARAM.XML"),
            authority="authoritative",
        )
        catalog = SourceCatalog(
            swmf_root=str(fake_swmf_root.resolve()),
            built_at_epoch_s=0.0,
            commands={"STOP": [stop_cmd]},
            components={"CON": ComponentVersion(component="CON", versions=[])},
            templates=[],
            scripts=[],
            idl_macros=[],
            source_files=[],
            idl_procedures={},
            resolution_notes=[],
        )
        monkeypatch.setattr(param_schema, "_load_catalog", lambda: (None, catalog))

        result = param_schema.get_param_schema_resource("STOP")
        assert result["ok"] is True
        # Existing contract fields must still be present
        assert "commands" in result
        assert "source_kinds" in result
        # New additive fields
        assert "source_evidence" in result
        assert "source_evidence_count" in result
        assert "source_evidence_note" in result


# ---------------------------------------------------------------------------
# Server registration contract
# ---------------------------------------------------------------------------


def test_knowledge_tools_registered_in_server() -> None:
    """Public knowledge tools are exported from the server module."""
    from swmf_mcp_server import server

    assert hasattr(server, "swmf_search_source")
    assert callable(getattr(server, "swmf_search_source"))
    assert hasattr(server, "swmf_lookup_source_symbol")
    assert callable(getattr(server, "swmf_lookup_source_symbol"))
    assert hasattr(server, "swmf_get_knowledge_index_status")
    assert callable(getattr(server, "swmf_get_knowledge_index_status"))
    assert not hasattr(server, "swmf_refresh_knowledge_index")
    assert not hasattr(server, "swmf_get_param_source_evidence")


# ---------------------------------------------------------------------------
# Multi-root indexing
# ---------------------------------------------------------------------------


@pytest.fixture()
def fake_swmfsolar_root(tmp_path: Path) -> Path:
    """A minimal fake SWMFSOLAR root with a Fortran file."""
    root = tmp_path / "SWMFSOLAR"
    src = root / "src"
    src.mkdir(parents=True)
    (src / "SC_session.f90").write_text(
        "! Solar corona session\nsubroutine ReadSolarParam(NameCommand)\n"
        "  use ModReadParam\n  select case(NameCommand)\n"
        "  case('#MAGNETOGRAM')\n    call read_var('iModel', iModel)\n"
        "  end select\nend subroutine ReadSolarParam\n",
        encoding="utf-8",
    )
    return root


class TestMultiRootIndexing:
    def test_extra_root_symbols_indexed(
        self, fake_swmf_root: Path, fake_swmfsolar_root: Path
    ) -> None:
        from swmf_mcp_server.catalog.source_index_catalog import (
            SLICE_SWMFSOLAR_SOURCE,
            SourceIndexCatalog,
        )

        catalog = SourceIndexCatalog(
            fake_swmf_root,
            extra_roots=[(fake_swmfsolar_root, SLICE_SWMFSOLAR_SOURCE)],
        )
        status = catalog.build(force=True)
        assert status.ok is True

        # Symbol from SWMFSOLAR must be found
        results = catalog.lookup_symbol("ReadSolarParam")
        assert len(results) >= 1
        assert results[0]["corpus_slice"] == SLICE_SWMFSOLAR_SOURCE

    def test_corpus_slice_filter_limits_to_one_root(
        self, fake_swmf_root: Path, fake_swmfsolar_root: Path
    ) -> None:
        from swmf_mcp_server.catalog.source_index_catalog import (
            SLICE_SWMF_SOURCE,
            SLICE_SWMFSOLAR_SOURCE,
            SourceIndexCatalog,
        )

        catalog = SourceIndexCatalog(
            fake_swmf_root,
            extra_roots=[(fake_swmfsolar_root, SLICE_SWMFSOLAR_SOURCE)],
        )
        catalog.build(force=True)

        solar = catalog.search_symbols("Param", corpus_slice=SLICE_SWMFSOLAR_SOURCE)
        assert all(r["corpus_slice"] == SLICE_SWMFSOLAR_SOURCE for r in solar)

        primary = catalog.search_symbols("Param", corpus_slice=SLICE_SWMF_SOURCE)
        assert all(r["corpus_slice"] == SLICE_SWMF_SOURCE for r in primary)

    def test_corpus_roots_in_status(
        self, fake_swmf_root: Path, fake_swmfsolar_root: Path
    ) -> None:
        from swmf_mcp_server.catalog.source_index_catalog import (
            SLICE_SWMFSOLAR_SOURCE,
            SourceIndexCatalog,
        )

        catalog = SourceIndexCatalog(
            fake_swmf_root,
            extra_roots=[(fake_swmfsolar_root, SLICE_SWMFSOLAR_SOURCE)],
        )
        catalog.build(force=True)
        status = catalog.get_status()
        assert str(fake_swmf_root) in status.corpus_roots
        assert str(fake_swmfsolar_root.resolve()) in status.corpus_roots

    def test_corpus_roots_in_status_payload(
        self, fake_swmf_root: Path, fake_swmfsolar_root: Path
    ) -> None:
        from swmf_mcp_server.catalog.source_index_catalog import (
            SLICE_SWMFSOLAR_SOURCE,
            SourceIndexCatalog,
        )

        catalog = SourceIndexCatalog(
            fake_swmf_root,
            extra_roots=[(fake_swmfsolar_root, SLICE_SWMFSOLAR_SOURCE)],
        )
        catalog.build(force=True)
        status = catalog.get_status()
        payload = ks.status_as_payload(status)
        assert "corpus_roots" in payload
        assert isinstance(payload["corpus_roots"], list)
        assert len(payload["corpus_roots"]) >= 2


# ---------------------------------------------------------------------------
# FTS5 full-text search
# ---------------------------------------------------------------------------


class TestFTS5Search:
    def test_fts5_finds_by_name(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build(force=True)
        results = catalog.search_symbols("CalcTimestep")
        assert any(r["name"] == "CalcTimestep" for r in results)

    def test_fts5_finds_by_docstring_keyword(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build(force=True)
        # "CFL" appears in CalcTimestep docstring
        results = catalog.search_symbols("CFL")
        assert len(results) >= 1

    def test_fts5_returns_ranked_results(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build(force=True)
        results = catalog.search_symbols("ReadParam", max_results=5)
        assert len(results) >= 1
        # No duplicates by name+file
        keys = [(r["name"], r["file_path"]) for r in results]
        assert len(keys) == len(set(keys))

    def test_search_kind_filter(self, fake_swmf_root: Path) -> None:
        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build(force=True)
        subroutines = catalog.search_symbols("Param", kind="subroutine")
        assert all(r["kind"] == "subroutine" for r in subroutines)


# ---------------------------------------------------------------------------
# Doc section indexing (tex / markdown)
# ---------------------------------------------------------------------------


class TestDocSectionIndexing:
    def test_markdown_file_indexed_as_doc_sections(self, fake_swmf_root: Path) -> None:
        # Write a markdown file under the fake root
        doc_dir = fake_swmf_root / "doc"
        doc_dir.mkdir(exist_ok=True)
        (doc_dir / "overview.md").write_text(
            "# Introduction\nThis is the overview.\n\n## Solver Details\nBATSRUS solver.\n",
            encoding="utf-8",
        )

        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build(force=True)

        results = catalog.search_symbols("Introduction")
        assert any(r["kind"] == "doc_section" for r in results)

    def test_tex_file_indexed_as_doc_sections(self, fake_swmf_root: Path) -> None:
        doc_dir = fake_swmf_root / "doc"
        doc_dir.mkdir(exist_ok=True)
        (doc_dir / "manual.tex").write_text(
            "\\section{User Guide}\nExplains how to set up BATS-R-US.\n"
            "\\subsection{Configuration}\nSee Config.pl.\n",
            encoding="utf-8",
        )

        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build(force=True)

        results = catalog.search_symbols("User Guide")
        assert any(r["kind"] == "doc_section" for r in results)

    def test_doc_section_corpus_slice_is_manuals(self, fake_swmf_root: Path) -> None:
        from swmf_mcp_server.catalog.source_index_catalog import SLICE_SWMF_MANUALS

        doc_dir = fake_swmf_root / "doc"
        doc_dir.mkdir(exist_ok=True)
        (doc_dir / "notes.md").write_text(
            "# Notes\nVarious notes about SWMF.\n",
            encoding="utf-8",
        )

        catalog = SourceIndexCatalog(fake_swmf_root)
        catalog.build(force=True)

        doc_results = catalog.search_symbols("Notes", kind="doc_section")
        if doc_results:
            # doc sections under a doc/ dir get swmf_manuals slice
            assert all(r["corpus_slice"] in (SLICE_SWMF_MANUALS, "analyst_context") for r in doc_results)
