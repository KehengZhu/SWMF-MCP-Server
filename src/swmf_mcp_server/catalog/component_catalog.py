from __future__ import annotations

from pathlib import Path

from ..core.models import ComponentVersion


def discover_component_versions(swmf_root: Path, xml_paths: list[Path]) -> dict[str, ComponentVersion]:
    components: dict[str, ComponentVersion] = {}
    resolved_root = swmf_root.resolve()

    for xml_path in xml_paths:
        try:
            rel = xml_path.resolve().relative_to(resolved_root)
        except ValueError:
            continue
        parts = rel.parts
        if len(parts) < 3 or parts[-1] != "PARAM.XML":
            continue
        component = parts[0]
        if len(component) != 2 or not component.isalnum():
            continue
        component = component.upper()
        version = xml_path.parent.name
        payload = components.setdefault(component, ComponentVersion(component=component, versions=[]))
        if version not in payload.versions:
            payload.versions.append(version)

    for payload in components.values():
        payload.versions.sort()

    return components
