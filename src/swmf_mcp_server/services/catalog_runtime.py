from __future__ import annotations

from typing import Any

from ..catalog.catalog_service import CatalogService
from ..core.errors import resolution_failure_payload
from ..core.models import SourceCatalog, SwmfRootResolution

_CATALOG_SERVICE: CatalogService = CatalogService()


def set_catalog_service(service: CatalogService) -> None:
    global _CATALOG_SERVICE
    _CATALOG_SERVICE = service


def get_source_catalog(
    root: SwmfRootResolution,
    force_refresh: bool = False,
) -> tuple[dict[str, Any] | None, SourceCatalog | None]:
    if not root.ok or root.swmf_root_resolved is None:
        return resolution_failure_payload(root.message or "Could not resolve SWMF root.", root.resolution_notes), None

    catalog = _CATALOG_SERVICE.get_catalog(
        swmf_root=root.swmf_root_resolved,
        resolution_notes=root.resolution_notes,
        force_refresh=force_refresh,
    )
    return None, catalog
