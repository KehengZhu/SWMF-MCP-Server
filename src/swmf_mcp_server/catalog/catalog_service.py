from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from ..core.models import CommandMetadata, SourceCatalog
from ..discovery.filesystem import file_mtime_map
from .component_catalog import discover_component_versions
from .idl_catalog import discover_idl_macros
from .script_catalog import discover_scripts
from .template_catalog import discover_example_params
from .xml_catalog import parse_param_xml_file


@dataclass
class _CacheEntry:
    catalog: SourceCatalog
    watched_paths: list[str]
    watched_mtimes: dict[str, float]


class CatalogService:
    def __init__(self) -> None:
        self._cache_by_root: dict[str, _CacheEntry] = {}

    def _watched_paths(
        self,
        swmf_root: Path,
        xml_paths: list[Path],
        scripts: list[str],
        templates: list[str],
    ) -> list[str]:
        watched: list[str] = [
            str(swmf_root.resolve()),
            str((swmf_root / "Param").resolve()),
            str((swmf_root / "PARAM").resolve()),
            str((swmf_root / "Examples").resolve()),
            str((swmf_root / "Scripts").resolve()),
        ]
        watched.extend(str(path.resolve()) for path in xml_paths)
        watched.extend(scripts)
        watched.extend(templates)
        return sorted(set(watched))

    def _is_cache_valid(self, cache: _CacheEntry) -> bool:
        return file_mtime_map(cache.watched_paths) == cache.watched_mtimes

    def _build_catalog(self, swmf_root: Path, resolution_notes: list[str] | None = None) -> SourceCatalog:
        xml_paths = sorted(swmf_root.rglob("PARAM.XML"))
        commands: dict[str, list[CommandMetadata]] = {}

        for xml_path in xml_paths:
            component: str | None = None
            try:
                rel = xml_path.resolve().relative_to(swmf_root.resolve())
                if len(rel.parts) >= 3 and rel.parts[-1] == "PARAM.XML":
                    maybe_component = rel.parts[0]
                    if len(maybe_component) == 2 and maybe_component.isalnum():
                        component = maybe_component.upper()
            except ValueError:
                component = None

            for entry in parse_param_xml_file(xml_path, component=component):
                commands.setdefault(entry.normalized, []).append(entry)

        components = discover_component_versions(swmf_root, xml_paths)
        templates = discover_example_params(swmf_root)
        scripts = discover_scripts(swmf_root)
        idl_macros = discover_idl_macros(swmf_root)

        source_files = sorted([str(path.resolve()) for path in xml_paths] + templates + scripts + idl_macros)

        return SourceCatalog(
            swmf_root=str(swmf_root.resolve()),
            built_at_epoch_s=time.time(),
            commands=commands,
            components=components,
            templates=templates,
            scripts=scripts,
            idl_macros=idl_macros,
            source_files=source_files,
            resolution_notes=resolution_notes or [],
        )

    def get_catalog(
        self,
        swmf_root: str,
        resolution_notes: list[str] | None = None,
        force_refresh: bool = False,
    ) -> SourceCatalog:
        root_path = Path(swmf_root).resolve()
        key = str(root_path)
        cache = self._cache_by_root.get(key)
        if (not force_refresh) and cache is not None and self._is_cache_valid(cache):
            return cache.catalog

        catalog = self._build_catalog(root_path, resolution_notes=resolution_notes)
        xml_paths = sorted(root_path.rglob("PARAM.XML"))
        watched = self._watched_paths(root_path, xml_paths, catalog.scripts, catalog.templates)
        self._cache_by_root[key] = _CacheEntry(
            catalog=catalog,
            watched_paths=watched,
            watched_mtimes=file_mtime_map(watched),
        )
        return catalog
