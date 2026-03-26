from __future__ import annotations

from ..models import SourceCatalog
from ..sources.template_catalog import find_examples_using_text
from ..sources.xml_catalog import normalize_command_name


def list_available_components(catalog: SourceCatalog) -> dict:
    payload = []
    for component, info in sorted(catalog.components.items()):
        payload.append({"component": component, "versions": info.versions})
    return {
        "ok": True,
        "authority": "authoritative",
        "source_kind": "component PARAM.XML",
        "swmf_root_resolved": catalog.swmf_root,
        "components": payload,
        "component_count": len(payload),
    }


def get_component_versions(catalog: SourceCatalog, component: str | None = None) -> dict:
    if component is None:
        return list_available_components(catalog)

    key = component.strip().upper()
    match = catalog.components.get(key)
    if match is None:
        return {
            "ok": False,
            "swmf_root_resolved": catalog.swmf_root,
            "message": f"No component versions found for component '{key}'.",
            "component": key,
            "authority": "authoritative",
            "source_kind": "component PARAM.XML",
        }

    return {
        "ok": True,
        "swmf_root_resolved": catalog.swmf_root,
        "component": key,
        "versions": match.versions,
        "authority": "authoritative",
        "source_kind": "component PARAM.XML",
    }


def find_param_command(catalog: SourceCatalog, name: str) -> dict:
    normalized = normalize_command_name(name)
    hits = catalog.commands.get(normalized, [])
    if not hits:
        return {
            "ok": False,
            "name": name,
            "normalized": normalized,
            "message": "No command found in indexed PARAM.XML sources.",
            "authority": "authoritative",
        }

    payload = []
    for item in hits:
        payload.append(
            {
                "name": item.name,
                "normalized": item.normalized,
                "owner_component": item.component,
                "description": item.description,
                "defaults": item.defaults,
                "allowed_values": item.allowed_values,
                "ranges": item.ranges,
                "source_kind": item.source_kind,
                "source_path": item.source_path,
                "authority": item.authority,
            }
        )

    return {
        "ok": True,
        "name": name,
        "normalized": normalized,
        "matches": payload,
        "match_count": len(payload),
        "swmf_root_resolved": catalog.swmf_root,
    }


def find_example_params(catalog: SourceCatalog, query: str, max_results: int = 30) -> dict:
    results = find_examples_using_text(catalog.templates, query=query, max_results=max_results)
    return {
        "ok": True,
        "query": query,
        "swmf_root_resolved": catalog.swmf_root,
        "source_kind": "example PARAM.in",
        "authority": "derived",
        "matches": results,
        "match_count": len(results),
    }


def trace_param_command(catalog: SourceCatalog, name: str, max_examples: int = 20) -> dict:
    command_payload = find_param_command(catalog, name=name)
    normalized = command_payload.get("normalized", normalize_command_name(name))
    examples_payload = find_example_params(catalog, query=normalized, max_results=max_examples)

    owners = sorted(
        {
            item.get("owner_component")
            for item in command_payload.get("matches", [])
            if item.get("owner_component")
        }
    )
    source_paths = sorted(
        {
            item.get("source_path")
            for item in command_payload.get("matches", [])
            if item.get("source_path")
        }
    )

    return {
        "ok": True,
        "name": name,
        "normalized": normalized,
        "defined_in": source_paths,
        "owner_components": owners,
        "example_usage_files": examples_payload.get("matches", []),
        "authorities": {
            "definition": "authoritative",
            "example_usage": "derived",
        },
        "sources": {
            "definitions": ["PARAM.XML", "component PARAM.XML"],
            "examples": ["example PARAM.in"],
        },
        "swmf_root_resolved": catalog.swmf_root,
    }
