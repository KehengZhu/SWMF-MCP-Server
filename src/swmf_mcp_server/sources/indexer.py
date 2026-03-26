from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from ..models import CommandMetadata, ComponentVersion, SourceCatalog
from .script_catalog import discover_scripts
from .template_catalog import discover_example_params
from .xml_catalog import parse_param_xml_file


@dataclass
class _CacheEntry:
    catalog: SourceCatalog
    watched_paths: list[str]
    watched_mtimes: dict[str, float]


class SourceIndexer:
    def __init__(self) -> None:
        self._cache_by_root: dict[str, _CacheEntry] = {}

    def _component_id_from_xml_path(self, swmf_root: Path, xml_path: Path) -> str | None:
        rel = xml_path.resolve().relative_to(swmf_root.resolve())
        parts = rel.parts
        if len(parts) >= 3 and parts[-1] == "PARAM.XML":
            maybe_component = parts[0]
            if len(maybe_component) == 2 and maybe_component.isalnum():
                return maybe_component.upper()
        return None

    def _watched_paths(self, swmf_root: Path, xml_paths: list[Path], scripts: list[str], templates: list[str]) -> list[str]:
        watched: list[str] = [
            str(swmf_root.resolve()),
            str((swmf_root / "Param").resolve()),
            str((swmf_root / "PARAM").resolve()),
            str((swmf_root / "Scripts").resolve()),
        ]
        watched.extend(str(path.resolve()) for path in xml_paths)
        watched.extend(scripts)
        watched.extend(templates)
        return sorted(set(watched))

    def _compute_mtime_map(self, paths: list[str]) -> dict[str, float]:
        mtimes: dict[str, float] = {}
        for path_text in paths:
            path = Path(path_text)
            try:
                mtimes[path_text] = path.stat().st_mtime
            except OSError:
                mtimes[path_text] = -1.0
        return mtimes

    def _is_cache_valid(self, cache: _CacheEntry) -> bool:
        current = self._compute_mtime_map(cache.watched_paths)
        return current == cache.watched_mtimes

    def _build_catalog(self, swmf_root: Path, resolution_notes: list[str] | None = None) -> SourceCatalog:
        xml_paths = sorted(swmf_root.rglob("PARAM.XML"))
        commands: dict[str, list[CommandMetadata]] = {}
        components: dict[str, ComponentVersion] = {}

        for xml_path in xml_paths:
            component = self._component_id_from_xml_path(swmf_root, xml_path)
            for entry in parse_param_xml_file(xml_path, component=component):
                commands.setdefault(entry.normalized, []).append(entry)

            if component is not None and len(xml_path.parts) >= 3:
                version = xml_path.parent.name
                existing = components.setdefault(component, ComponentVersion(component=component, versions=[]))
                if version not in existing.versions:
                    existing.versions.append(version)

        for payload in components.values():
            payload.versions.sort()

        templates = discover_example_params(swmf_root)
        scripts = discover_scripts(swmf_root)

        idl_macros: list[str] = []
        idl_dir = swmf_root / "share" / "IDL"
        if idl_dir.is_dir():
            for path in idl_dir.rglob("*.pro"):
                idl_macros.append(str(path.resolve()))
                if len(idl_macros) >= 1000:
                    break

        source_files = sorted(
            [str(path.resolve()) for path in xml_paths] + templates + scripts + idl_macros
        )

        return SourceCatalog(
            swmf_root=str(swmf_root.resolve()),
            built_at_epoch_s=time.time(),
            commands=commands,
            components=components,
            templates=templates,
            scripts=scripts,
            idl_macros=sorted(idl_macros),
            source_files=source_files,
            resolution_notes=resolution_notes or [],
        )

    def get_catalog(self, swmf_root: str, resolution_notes: list[str] | None = None, force_refresh: bool = False) -> SourceCatalog:
        root_path = Path(swmf_root).resolve()
        root_key = str(root_path)
        cache = self._cache_by_root.get(root_key)
        if (not force_refresh) and cache is not None and self._is_cache_valid(cache):
            return cache.catalog

        catalog = self._build_catalog(root_path, resolution_notes=resolution_notes)
        watched_paths = self._watched_paths(root_path, sorted(root_path.rglob("PARAM.XML")), catalog.scripts, catalog.templates)
        watched_mtimes = self._compute_mtime_map(watched_paths)
        self._cache_by_root[root_key] = _CacheEntry(
            catalog=catalog,
            watched_paths=watched_paths,
            watched_mtimes=watched_mtimes,
        )
        return catalog
