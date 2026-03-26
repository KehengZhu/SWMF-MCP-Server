from __future__ import annotations

from typing import Literal


Authority = Literal["heuristic", "derived", "authoritative"]

AUTHORITY_HEURISTIC: Authority = "heuristic"
AUTHORITY_DERIVED: Authority = "derived"
AUTHORITY_AUTHORITATIVE: Authority = "authoritative"

SOURCE_KIND_CURATED = "curated"
SOURCE_KIND_PARAM_XML = "PARAM.XML"
SOURCE_KIND_COMPONENT_PARAM_XML = "component PARAM.XML"
SOURCE_KIND_EXAMPLE_PARAM = "example PARAM.in"
SOURCE_KIND_SCRIPT = "script"
SOURCE_KIND_LIGHTWEIGHT_PARSER = "lightweight_parser"
