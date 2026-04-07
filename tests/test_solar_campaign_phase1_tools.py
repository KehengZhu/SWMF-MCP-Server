from __future__ import annotations

from pathlib import Path

from swmf_mcp_server import server


_EVENT_LIST_TEXT = "\n".join(
    [
        "selected run IDs = 1,3",
        "#START",
        "ID params",
        "1 map=GONG_CR2208.fits model=AWSoM",
        "2 map=ADAPT_CR2208.fits model=AWSoM realization=[1,2-3]",
        "3 map=ADAPT_CR2209.fits model=AWSoMR POYNTINGFLUX=[5e5] BrFactor=2.0 add=CHANGEWEAKFIELD rm=HARMONICSGRID",
    ]
)


def test_parse_solar_event_list_basic() -> None:
    result = server.swmf_parse_solar_event_list(event_list_text=_EVENT_LIST_TEXT)

    assert result["ok"] is True
    assert result["phase"] == "parse"
    assert result["selected_run_ids"] == [1, 3]
    assert result["selected_run_count"] == 2

    run1 = result["selected_runs"][0]
    run3 = result["selected_runs"][1]

    assert run1["model"] == "AWSoM"
    assert run1["realizations"] == [1]
    assert run3["model"] == "AWSoMR"
    assert run3["realizations"] == list(range(1, 13))
    assert run3["param_mutations"]["replace"]["POYNTINGFLUX"] == "5e5"
    assert run3["param_mutations"]["change"]["BrFactor"] == "2.0"
    assert run3["param_mutations"]["add"] == ["CHANGEWEAKFIELD"]
    assert run3["param_mutations"]["rm"] == ["HARMONICSGRID"]


def test_parse_solar_event_list_selected_override() -> None:
    result = server.swmf_parse_solar_event_list(
        event_list_text=_EVENT_LIST_TEXT,
        selected_run_ids="2-3",
    )

    assert result["ok"] is True
    assert result["selected_run_ids"] == [2, 3]
    assert result["selected_run_ids_source"] == "override"
    assert [item["run_id"] for item in result["selected_runs"]] == [2, 3]
    assert result["selected_runs"][0]["realizations"] == [1, 2, 3]


def test_plan_solar_campaign_dry_run_preview(tmp_path: Path) -> None:
    swmfsolar = tmp_path / "SWMFSOLAR"
    (swmfsolar / "Scripts").mkdir(parents=True)
    (swmfsolar / "Events").mkdir(parents=True)
    (swmfsolar / "Makefile").write_text("all:\n\t@echo ok\n", encoding="utf-8")

    event_path = swmfsolar / "Events" / "param_list.txt"
    event_path.write_text(_EVENT_LIST_TEXT + "\n", encoding="utf-8")

    result = server.swmf_plan_solar_campaign(
        event_list_path=str(event_path),
        run_dir=str(tmp_path),
    )

    assert result["ok"] is True
    assert result["phase"] == "plan_only"
    assert result["requires_manual_execution"] is True
    assert result["execute_supported"] is False
    assert result["swmfsolar_root_resolved"] == str(swmfsolar.resolve())

    compile_group = result["command_groups"]["compile"]
    assert compile_group[0] == "make compile DOINSTALL=T MODEL=AWSoM"
    assert compile_group[1] == "make compile DOINSTALL=F MODEL=AWSoMR"

    assert result["command_preview"][0] == f"cd {swmfsolar.resolve()}"
    assert len(result["runs"]) == 2
    assert any("make rundir_realizations" in cmd for cmd in result["runs"][0]["command_groups"]["prepare_shell"])
    assert result["runs"][0]["command_groups"]["submit_shell"]


def test_plan_solar_campaign_without_submit_commands() -> None:
    result = server.swmf_plan_solar_campaign(
        event_list_text=_EVENT_LIST_TEXT,
        include_submit_commands=False,
    )

    assert result["ok"] is True
    assert result["command_groups"]["submit"] == []
    assert all(item["command_groups"]["submit_shell"] == [] for item in result["runs"])
