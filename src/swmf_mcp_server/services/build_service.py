from __future__ import annotations

from ..parsing.param_parser import parse_param_text

COMPONENT_VERSION_DEFAULTS: dict[str, str] = {
    "GM": "GM/BATSRUS",
    "SC": "SC/BATSRUS",
    "IE": "IE/Ridley_serial",
    "IM": "IM/RCM2",
    "IH": "IH/BATSRUS",
    "OH": "OH/BATSRUS",
    "UA": "UA/GITM",
    "EE": "EE/Empty",
}


def _normalize_component_list(components_csv: str) -> list[str]:
    items = [item.strip() for item in components_csv.split(",") if item.strip()]
    deduped: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def _infer_required_components_from_sessions(sessions: list) -> list[str]:
    required: list[str] = []
    seen: set[str] = set()

    def add_component(comp: str) -> None:
        comp_id = comp.strip().upper()
        if len(comp_id) != 2:
            return
        if comp_id not in seen:
            seen.add(comp_id)
            required.append(comp_id)

    for session in sessions:
        for row in session.component_map_rows:
            add_component(str(row.get("component", "")))
        for comp in session.component_blocks:
            add_component(comp)
        for comp, _ in session.switched_components:
            add_component(comp)

    return required


def _build_component_config_recommendation(required_components: list[str]) -> dict:
    versions: list[str] = []
    missing_defaults: list[str] = []

    for comp in required_components:
        version = COMPONENT_VERSION_DEFAULTS.get(comp)
        if version is None:
            missing_defaults.append(comp)
        else:
            versions.append(version)

    config_command = f"./Config.pl -v={','.join(['Empty'] + versions)}"
    warnings = [f"No prototype default version mapping is defined for component {comp}." for comp in missing_defaults]

    return {
        "required_components": required_components,
        "recommended_component_versions": versions,
        "components_without_default_mapping": missing_defaults,
        "recommended_config_command": config_command,
        "rebuild_commands": ["make clean", "make -j"],
        "warnings": warnings,
    }


def prepare_build(
    components_csv: str,
    compiler: str | None = None,
    debug: bool = False,
    optimization: int | None = None,
) -> dict:
    requested = _normalize_component_list(components_csv)
    if not requested:
        return {
            "ok": False,
            "message": "Provide at least one component version, e.g. GM/BATSRUS,IE/Ridley_serial",
        }

    version_list = ["Empty"] + [item for item in requested if item.lower() != "empty"]
    version_arg = ",".join(version_list)

    commands: list[str] = []
    commands.append(f"./Config.pl -install -compiler={compiler}" if compiler else "./Config.pl -install")
    commands.append(f"Config.pl -v={version_arg}")

    if optimization is None:
        optimization = 0 if debug else 4

    commands.append(f"Config.pl {'-debug' if debug else '-nodebug'} -O{optimization}")
    commands.append("Config.pl -show")
    commands.append("make -j")

    return {
        "ok": True,
        "selected_components": requested,
        "config_pl_v_argument": version_arg,
        "suggested_commands": commands,
        "authority": "heuristic",
        "source_kind": "curated",
        "source_paths": [],
        "notes": [
            "The prototype returns suggested commands only. It does not execute them.",
            "Putting Empty first follows standard SWMF usage for 'all empty except selected components'.",
            "After changing compiler flags, a real workflow may also need make clean before recompiling.",
        ],
    }


def prepare_component_config(
    param_text: str,
) -> dict:
    parsed = parse_param_text(param_text)
    recommendation = _build_component_config_recommendation(_infer_required_components_from_sessions(parsed.sessions))
    return {
        "ok": True,
        "authority": "heuristic",
        "source_kind": "lightweight_parser",
        "source_paths": [],
        "required_components": recommendation["required_components"],
        "recommended_component_versions": recommendation["recommended_component_versions"],
        "components_without_default_mapping": recommendation["components_without_default_mapping"],
        "recommended_config_command": recommendation["recommended_config_command"],
        "rebuild_commands": recommendation["rebuild_commands"],
        "warnings": recommendation["warnings"],
    }


def explain_component_config_fix() -> dict:
    return {
        "ok": True,
        "authority": "heuristic",
        "source_kind": "curated",
        "source_paths": [],
        "title": "Why Config.pl -v is needed for real components",
        "explanation": [
            "#COMPONENTMAP and component blocks reference active SWMF components such as SC or GM.",
            "If SWMF is compiled with only Empty versions for those components, validation and runtime checks can fail for missing component versions.",
            "Use Config.pl -v=Empty,<non-empty component versions...> to compile the component implementations required by PARAM.in.",
            "After changing component selections, rebuild with make clean and make -j.",
        ],
        "example": {
            "required_components": ["SC"],
            "recommended_config_command": "./Config.pl -v=Empty,SC/BATSRUS",
            "rebuild_commands": ["make clean", "make -j"],
        },
    }
