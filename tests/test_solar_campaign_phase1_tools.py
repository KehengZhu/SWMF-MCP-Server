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


def test_parse_solar_event_list_missing_path_returns_path_hints(tmp_path: Path) -> None:
    result = server.swmf_parse_solar_event_list(
        event_list_path=str(tmp_path / "missing_param_list.txt"),
        run_dir=str(tmp_path),
    )

    assert result["ok"] is False
    assert result["error_code"] == "EVENT_LIST_LOAD_FAILED"
    assert result["path_search_hints"]
    assert "path_search_roots" in result


def test_plan_solar_campaign_dry_run_preview(tmp_path: Path) -> None:
    swmfsolar = tmp_path / "SWMFSOLAR"
    (swmfsolar / "Scripts").mkdir(parents=True)
    (swmfsolar / "Events").mkdir(parents=True)
    (swmfsolar / "README").write_text(
        "SWMFSOLAR must be linked to an installed SWMF source code directory.\n"
        "It is required to have the symbolic link of SWMF to the installed SWMF.\n",
        encoding="utf-8",
    )
    (swmfsolar / "Makefile").write_text(
        "\n".join(
            [
                "MODEL = AWSoM",
                "MACHINE = frontera",
                "POYNTINGFLUX = -1.0",
                "JOBNAME = amap",
                "help:",
                '\t@echo " MODEL=AWSoM - select model"',
                'run:',
                '\t@if [[ "${MACHINE}" == "frontera" ]]; then sbatch job.long; fi',
                "rundir_local:",
                "\t@echo prep",
                "adapt_run:",
                "\tmake rundir_local",
                "\tmake run",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    event_path = swmfsolar / "Events" / "param_list.txt"
    event_path.write_text(_EVENT_LIST_TEXT + "\n", encoding="utf-8")

    result = server.swmf_plan_solar_campaign(
        event_list_path=str(event_path),
        run_dir=str(tmp_path),
    )

    assert result["ok"] is True
    assert result["phase"] == "plan_only"
    assert result["guidance_mode"] == "instruction_first"
    assert result["requires_manual_execution"] is True
    assert result["execute_supported"] is False
    assert result["swmfsolar_root_resolved"] == str(swmfsolar.resolve())
    assert result["workflow_guidance"]
    assert result["decision_branches"]
    assert "MODEL" in result["variable_guidance"]
    assert "optional_command_examples" in result
    assert "target_recipes" in result
    assert "scheduler_branches" in result
    assert "environment_prerequisites" in result
    assert "rundir_local" in result["target_recipes"].get("adapt_run", [])
    assert any(item.get("machine") == "frontera" for item in result["scheduler_branches"])
    assert any("required" in item.lower() or "must" in item.lower() for item in result["environment_prerequisites"])
    assert str((swmfsolar / "README").resolve()) in result["source_paths"]

    compile_group = result["optional_command_examples"]["compile"]
    assert compile_group[0] == "make compile DOINSTALL=T MODEL=AWSoM"
    assert compile_group[1] == "make compile DOINSTALL=F MODEL=AWSoMR"

    assert result["optional_command_examples"]["full_sequence"][0] == f"cd {swmfsolar.resolve()}"
    assert len(result["runs"]) == 2
    assert any("make rundir_realizations" in cmd for cmd in result["runs"][0]["optional_command_examples"]["prepare_shell"])
    assert result["runs"][0]["optional_command_examples"]["submit_shell"]
    assert result["runs"][0]["workflow_guidance"]
    assert result["runs"][0]["decision_branches"]
    assert "MODEL" in result["runs"][0]["variable_guidance"]
    assert "optional_command_examples" in result["runs"][0]

    adapt_group = result["optional_command_examples"]["adapt_run"]
    assert len(adapt_group) == 2
    assert adapt_group[0].startswith("make adapt_run MODEL=AWSoM ")
    assert "MACHINE=frontera" in adapt_group[0]
    assert "POYNTINGFLUX=-1.0" in adapt_group[0]
    assert "JOBNAME=amap" in adapt_group[0]
    assert "POYNTINGFLUX=5e5" in adapt_group[1]
    assert result["runs"][0]["optional_command_examples"]["adapt_run_shell"]


def test_plan_solar_campaign_without_submit_commands() -> None:
    result = server.swmf_plan_solar_campaign(
        event_list_text=_EVENT_LIST_TEXT,
        include_submit_commands=False,
    )

    assert result["ok"] is True
    assert result["guidance_mode"] == "instruction_first"
    assert result["optional_command_examples"]["submit"] == []
    assert result["optional_command_examples"]["adapt_run"] == []
    assert result["workflow_guidance"]
    assert result["decision_branches"]
    assert all(item["optional_command_examples"]["submit_shell"] == [] for item in result["runs"])
    assert all(item["optional_command_examples"]["adapt_run_shell"] == [] for item in result["runs"])
