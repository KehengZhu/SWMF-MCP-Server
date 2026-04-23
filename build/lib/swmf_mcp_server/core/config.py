from __future__ import annotations

SWMF_ROOT_ENV = "SWMF_ROOT"
DEFAULT_QUICKRUN_NPROC = 64
DEFAULT_COMMAND_TIMEOUT_S = 600


def swmf_root_markers() -> list[str]:
    return ["Config.pl", "PARAM.XML", "Scripts/TestParam.pl"]
