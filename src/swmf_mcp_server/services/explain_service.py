from __future__ import annotations

from ..catalog.xml_catalog import normalize_command_name
from ..core.authority import AUTHORITY_DERIVED, AUTHORITY_HEURISTIC, SOURCE_KIND_CURATED
from ..core.models import SourceCatalog, SourceRef
from ..knowledge.curated import CURATED_KNOWLEDGE, normalize_curated_lookup_key


def explain_param(name: str, catalog: SourceCatalog | None) -> dict:
    if catalog is None:
        key = normalize_curated_lookup_key(name)
        curated = CURATED_KNOWLEDGE.get(key)
        if curated is None:
            return {
                "found": False,
                "name": name,
                "message": "No command match found in curated knowledge.",
                "authority": AUTHORITY_HEURISTIC,
                "source_kind": SOURCE_KIND_CURATED,
                "source_paths": [],
                "source_kinds": [SOURCE_KIND_CURATED],
            }

        return {
            "found": True,
            "name": curated["title"],
            "summary": curated.get("summary"),
            "details": curated.get("details"),
            "aliases": curated.get("aliases", []),
            "authority": AUTHORITY_HEURISTIC,
            "source_kind": SOURCE_KIND_CURATED,
            "source_paths": [],
            "source_kinds": [SOURCE_KIND_CURATED],
            "sources": [{"kind": SOURCE_KIND_CURATED, "path": None, "authority": AUTHORITY_HEURISTIC}],
        }

    normalized = normalize_command_name(name)
    command_hits = catalog.commands.get(normalized, [])
    sources: list[SourceRef] = []

    curated_key = normalize_curated_lookup_key(name)
    curated = CURATED_KNOWLEDGE.get(curated_key)

    authority = AUTHORITY_HEURISTIC
    source_kind = SOURCE_KIND_CURATED
    title = name
    summary = None
    details = None
    defaults: dict[str, str] = {}
    allowed_values: list[str] = []
    ranges: list[str] = []
    aliases: list[str] = []
    owners: list[str] = []

    if command_hits:
        authority = "authoritative"
        source_kind = command_hits[0].source_kind
        first = command_hits[0]
        title = first.normalized
        summary = first.description

        for hit in command_hits:
            if hit.component and hit.component not in owners:
                owners.append(hit.component)
            defaults.update(hit.defaults)
            allowed_values.extend(item for item in hit.allowed_values if item not in allowed_values)
            ranges.extend(item for item in hit.ranges if item not in ranges)
            sources.append(SourceRef(kind=hit.source_kind, path=hit.source_path, authority=hit.authority))

    if curated is not None:
        title = curated.get("title", title)
        if summary is None:
            summary = curated.get("summary")
        details = curated.get("details")
        aliases.extend(curated.get("aliases", []))
        sources.append(SourceRef(kind=SOURCE_KIND_CURATED, path=None, authority=AUTHORITY_HEURISTIC))
        if authority == AUTHORITY_HEURISTIC:
            authority = AUTHORITY_DERIVED

    if not command_hits and curated is None:
        return {
            "found": False,
            "name": name,
            "message": "No command match found in curated or indexed SWMF sources.",
            "authority": AUTHORITY_HEURISTIC,
            "source_kind": SOURCE_KIND_CURATED,
            "source_paths": [],
            "source_kinds": [SOURCE_KIND_CURATED],
        }

    seen: set[tuple[str, str | None, str]] = set()
    source_payload: list[dict] = []
    for item in sources:
        key = (item.kind, item.path, item.authority)
        if key in seen:
            continue
        seen.add(key)
        source_payload.append({"kind": item.kind, "path": item.path, "authority": item.authority})

    source_paths = [item["path"] for item in source_payload if item["path"]]
    source_kinds = sorted({item["kind"] for item in source_payload})

    return {
        "found": True,
        "name": title,
        "normalized": normalized,
        "summary": summary,
        "details": details,
        "aliases": sorted(set(aliases)),
        "owner_components": owners,
        "defaults": defaults,
        "allowed_values": allowed_values,
        "ranges": ranges,
        "source_paths": source_paths,
        "source_kind": source_kind,
        "source_kinds": source_kinds,
        "sources": source_payload,
        "authority": authority,
    }
