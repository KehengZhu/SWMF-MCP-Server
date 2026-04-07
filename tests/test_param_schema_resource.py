from __future__ import annotations

from pathlib import Path

from swmf_mcp_server.core.models import CommandMetadata, ComponentVersion, SourceCatalog
from swmf_mcp_server.resources import param_schema


def _fake_catalog(tmp_path: Path) -> SourceCatalog:
    root = tmp_path / "SWMF"
    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "SWMF.md").write_text(
        """
# SWMF Manual

CME workflows can restart from background solar wind runs.
Use Restart.pl -i -v RESTART_TREE for linking restart inputs.
""".strip()
        + "\n",
        encoding="utf-8",
    )

    tex_dir = root / "doc" / "Tex"
    tex_dir.mkdir(parents=True)
    (tex_dir / "SWMF_param.tex").write_text(
        r"""
\section{CME Setup}
Use Restart.pl -i -v RESTART_TREE for restart linking.
Set \textbf{CME} launch parameters in PARAM.in.
""".strip()
        + "\n",
        encoding="utf-8",
    )

    cme_cmd = CommandMetadata(
        name="#CME",
        normalized="CME",
        component="SC",
        description="Set CME launch parameters",
        defaults={"Speed": "1200"},
        allowed_values=["TT", "TD"],
        ranges=["Speed > 0"],
        source_kind="component PARAM.XML",
        source_path=str((root / "SC" / "PARAM.XML").resolve()),
        authority="authoritative",
    )
    time_cmd = CommandMetadata(
        name="#TIMEACCURATE",
        normalized="TIMEACCURATE",
        component="CON",
        description="Switch time accurate mode on or off",
        source_kind="PARAM.XML",
        source_path=str((root / "PARAM.XML").resolve()),
        authority="authoritative",
    )

    return SourceCatalog(
        swmf_root=str(root.resolve()),
        built_at_epoch_s=0.0,
        commands={"CME": [cme_cmd], "TIMEACCURATE": [time_cmd]},
        components={"SC": ComponentVersion(component="SC", versions=["BATSRUS"])},
        templates=[],
        scripts=[],
        idl_macros=[],
        source_files=[],
        idl_procedures={},
        resolution_notes=[],
    )


def test_param_schema_keyword_query_includes_manual_context(monkeypatch, tmp_path: Path) -> None:
    catalog = _fake_catalog(tmp_path)
    monkeypatch.setattr(param_schema, "_load_catalog", lambda: (None, catalog))

    result = param_schema.get_param_schema_resource("CME")

    assert result["ok"] is True
    assert result["query_mode"] == "keyword"
    assert result["count"] >= 1
    assert result["manual_context_count"] >= 1
    assert any("SWMF.md" in path or "SWMF_param.tex" in path for path in result["source_paths"])
    assert any(entry.get("source_kind") in {"manual/docs", "manual/tex"} for entry in result["manual_context"])


def test_param_schema_keyword_query_reads_tex_manuals(monkeypatch, tmp_path: Path) -> None:
    catalog = _fake_catalog(tmp_path)
    monkeypatch.setattr(param_schema, "_load_catalog", lambda: (None, catalog))

    result = param_schema.get_param_schema_resource("restart")

    assert result["ok"] is True
    assert result["query_mode"] == "keyword"
    assert any(entry.get("source_kind") == "manual/tex" for entry in result["manual_context"])
    assert any("SWMF_param.tex" in entry.get("path", "") for entry in result["manual_context"])


def test_param_schema_component_query_still_supported(monkeypatch, tmp_path: Path) -> None:
    catalog = _fake_catalog(tmp_path)
    monkeypatch.setattr(param_schema, "_load_catalog", lambda: (None, catalog))

    result = param_schema.get_param_schema_resource("SC")

    assert result["ok"] is True
    assert result["query_mode"] == "component"
    assert result["count"] == 1
    assert result["commands"][0]["normalized"] == "CME"
    assert result["manual_context_count"] == 0
