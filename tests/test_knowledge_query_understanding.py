from __future__ import annotations

from pathlib import Path

import pytest

from swmf_mcp_server.catalog.source_index_catalog import (
    SLICE_SWMF_MANUALS,
    SLICE_SWMF_PARAM_XML,
    SLICE_SWMF_SOURCE,
    SLICE_SWMFSOLAR_SOURCE,
)
from swmf_mcp_server.knowledge.service import get_agent_context_pack, understand_source_query


@pytest.fixture()
def fake_swmf_root(tmp_path: Path) -> Path:
    root = tmp_path / "SWMF"
    (root / "Scripts").mkdir(parents=True)
    (root / "share" / "IDL").mkdir(parents=True)
    (root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
    (root / "Scripts" / "TestParam.pl").write_text(
        "#!/usr/bin/env perl\nsub TestParam { }\n",
        encoding="utf-8",
    )
    (root / "PARAM.XML").write_text(
        "<commandList>\n"
        '  <command name="#STOP" type="real" default="3600.0">Stop criteria.</command>\n'
        "</commandList>\n",
        encoding="utf-8",
    )

    src = root / "src"
    src.mkdir()
    (src / "CON_session.f90").write_text(
        "subroutine ReadParam(NameCommand)\n"
        "  select case(NameCommand)\n"
        "  case('#STOP')\n"
        "  end select\n"
        "end subroutine ReadParam\n",
        encoding="utf-8",
    )

    gm_root = root / "GM" / "BATSRUS"
    (gm_root / "src").mkdir(parents=True)
    (gm_root / "PARAM.XML").write_text(
        "<commandList>\n"
        '  <command name="#TIMESTEP" type="real" default="0.5" />\n'
        "</commandList>\n",
        encoding="utf-8",
    )

    (root / "share" / "IDL" / "plot_test.pro").write_text(
        "pro plot_test, value\n"
        "  print, value\n"
        "end\n",
        encoding="utf-8",
    )
    return root


def test_understand_source_query_classifies_param_lookup() -> None:
    payload = understand_source_query("Explain #STOP handling in ReadParam for GM")

    assert payload["intent"] == "param_lookup"
    assert payload["preferred_search_mode"] == "keyword"
    assert payload["entities"]["components"] == ["GM"]
    assert payload["entities"]["param_commands"] == ["#STOP"]
    assert "ReadParam" in payload["entities"]["symbol_hints"]
    assert payload["recommended_corpus_slices"][:2] == [SLICE_SWMF_PARAM_XML, "swmf_scripts"]
    assert SLICE_SWMF_SOURCE in payload["recommended_corpus_slices"]


def test_understand_source_query_keeps_keyword_for_coupling_questions() -> None:
    # Semantic / hybrid retrieval has been removed; every intent now maps to
    # the keyword backend, but the coupling-question classifier and the
    # corpus-slice recommendations should still fire correctly.
    payload = understand_source_query("How does IH couple to SC during magnetogram workflows?")

    assert payload["intent"] == "coupling_analysis"
    assert payload["preferred_search_mode"] == "keyword"
    assert payload["entities"]["components"] == ["IH", "SC"]
    assert SLICE_SWMF_SOURCE in payload["recommended_corpus_slices"]
    assert SLICE_SWMF_MANUALS in payload["recommended_corpus_slices"]
    assert SLICE_SWMFSOLAR_SOURCE in payload["recommended_corpus_slices"]


def test_get_agent_context_pack_combines_search_and_reference(fake_swmf_root: Path) -> None:
    pack = get_agent_context_pack(str(fake_swmf_root), "Explain #STOP handling in ReadParam for GM")

    assert pack["ok"] is True
    assert pack["query_analysis"]["intent"] == "param_lookup"
    assert pack["grounded_context"]["briefing"]["focus_commands"] == ["#STOP"]
    assert pack["grounded_context"]["reference_context"]["param_commands"][0]["definition"]["ok"] is True
    # semantic_runtime has been removed from search_strategy; search_method
    # is now always "keyword".
    assert "semantic_runtime" not in pack["search_strategy"]
    assert pack["search_strategy"]["search_method"] == "keyword"
    assert any(item["file_path"].endswith("CON_session.f90") for item in pack["grounded_context"]["evidence"])


def test_get_agent_context_pack_includes_idl_reference(fake_swmf_root: Path) -> None:
    pack = get_agent_context_pack(str(fake_swmf_root), "Explain plot_test IDL procedure")

    assert pack["ok"] is True
    idl_context = pack["grounded_context"]["reference_context"]["idl_procedures"]
    assert len(idl_context) == 1
    assert idl_context[0]["name"] == "plot_test"
