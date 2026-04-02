from typing import Any

from ..core.errors import resolution_failure_payload
from ..core.models import SourceCatalog, SwmfRootResolution
from .catalog_service import CatalogService
from .component_catalog import discover_component_versions
from .idl_catalog import discover_idl_macros, discover_idl_procedures, get_idl_procedure, list_idl_procedures
from .script_catalog import discover_scripts
from .template_catalog import discover_example_params, find_examples_using_text
from .xml_catalog import normalize_command_name, parse_param_xml_file

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

__all__ = [
    "CatalogService",
    "get_source_catalog",
    "discover_component_versions",
    "discover_idl_macros",
    "discover_idl_procedures",
    "discover_scripts",
    "discover_example_params",
    "get_idl_procedure",
    "find_examples_using_text",
    "list_idl_procedures",
    "normalize_command_name",
    "parse_param_xml_file",
    "set_catalog_service",
]
