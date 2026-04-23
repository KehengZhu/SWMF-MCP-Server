from __future__ import annotations

from typing import Any

CURATED_KNOWLEDGE: dict[str, dict[str, Any]] = {
    "#COMPONENTMAP": {
        "title": "#COMPONENTMAP",
        "summary": "Registers active components for a run and defines their processor layout.",
        "details": (
            "This is the primary run-time component layout command. It selects which non-empty "
            "components participate in the run and assigns MPI ranks (and optionally threading layout) "
            "to each component. It is usually one of the first things to inspect when diagnosing bad "
            "nproc choices, idle ranks, overlap/concurrency issues, or component-registration failures."
        ),
        "see_also": ["#COMPONENT", "#CYCLE", "#COUPLE2", "Scripts/TestParam.pl", "PARAM.XML"],
        "aliases": ["COMPONENTMAP", "componentmap", "processor layout", "rank layout"],
        "tags": ["control", "layout", "execution", "parallel"],
    },
    "#COMPONENT": {
        "title": "#COMPONENT",
        "summary": "Turns a registered component on or off within a session.",
        "details": (
            "Use this when a component is present in #COMPONENTMAP but should be disabled for a given "
            "session. This is useful for staged runs where components are enabled later after an initial "
            "relaxation or startup phase."
        ),
        "see_also": ["#COMPONENTMAP", "#RUN", "#STOP"],
        "aliases": ["COMPONENT", "component on off", "UseComp"],
        "tags": ["control", "sessions"],
    },
    "#TIMEACCURATE": {
        "title": "#TIMEACCURATE",
        "summary": "Selects time-accurate or steady-state execution for a session.",
        "details": (
            "Time-accurate mode advances physical simulation time. Steady-state mode is iteration-centric "
            "and commonly relies on component/coupling frequencies for convergence behavior. A common "
            "diagnostic question is whether #STOP and restart/output frequencies are being interpreted "
            "in time units or iteration units."
        ),
        "see_also": ["#STOP", "#CYCLE", "#SAVERESTART"],
        "aliases": ["TIMEACCURATE", "timeaccurate", "steady state", "DoTimeAccurate"],
        "tags": ["control", "time", "sessions"],
    },
    "#STOP": {
        "title": "#STOP",
        "summary": "Defines stop limits for the current session.",
        "details": (
            "In steady-state sessions MaxIteration is the key stop control. In time-accurate sessions "
            "tSimulationMax is the key stop control. In multi-session runs, stop values are interpreted "
            "cumulatively across the run, so confusion here often leads to unexpected run length."
        ),
        "see_also": ["#TIMEACCURATE", "#RUN", "#END"],
        "aliases": ["STOP", "stop", "MaxIteration", "tSimulationMax"],
        "tags": ["control", "time", "sessions"],
    },
    "#RUN": {
        "title": "#RUN",
        "summary": "Ends the current session and starts execution with the parameters accumulated so far.",
        "details": (
            "SWMF executes runs in consecutive sessions. Parameters carry forward, so later sessions only "
            "need to specify changes. This makes #RUN one of the key anchors for explaining staged run setup."
        ),
        "see_also": ["#STOP", "#COMPONENT", "#INCLUDE"],
        "aliases": ["RUN", "run session"],
        "tags": ["control", "sessions"],
    },
    "#INCLUDE": {
        "title": "#INCLUDE",
        "summary": "Includes another parameter file into PARAM.in.",
        "details": (
            "Used to factor runs into reusable fragments such as restart includes, shared component blocks, "
            "or scenario templates. Nested includes are supported. This is a core concept for real SWMF "
            "jobs because many production PARAM.in files are layered rather than monolithic."
        ),
        "see_also": ["PARAM.in", "RESTART.in", "#BEGIN_COMP"],
        "aliases": ["INCLUDE", "include", "include file", "RESTART.in"],
        "tags": ["param", "structure", "reuse"],
    },
    "#BEGIN_COMP": {
        "title": "#BEGIN_COMP / #END_COMP",
        "summary": "Delimits a component-specific parameter block inside PARAM.in.",
        "details": (
            "Lines inside the block are passed to the addressed component. These blocks are where MCP "
            "should expect component PARAM.XML semantics to apply. Misplaced component commands often "
            "reduce to block-boundary or include-structure mistakes."
        ),
        "see_also": ["PARAM.XML", "component PARAM.XML", "#INCLUDE"],
        "aliases": ["BEGIN_COMP", "END_COMP", "component block", "component section"],
        "tags": ["param", "components", "structure"],
    },
    "#CYCLE": {
        "title": "#CYCLE",
        "summary": "Controls how often a component is executed relative to SWMF steps.",
        "details": (
            "Especially important in steady-state workflows, where different components may need different "
            "relative calling frequencies for stability and convergence. This is a high-value troubleshooting "
            "concept even though the authoritative parameter definition still belongs in PARAM.XML."
        ),
        "see_also": ["#TIMEACCURATE", "#COUPLE2", "#COMPONENTMAP"],
        "aliases": ["CYCLE", "DnRun", "component frequency"],
        "tags": ["execution", "steady-state", "coupling"],
    },
    "#COUPLE2": {
        "title": "#COUPLE2",
        "summary": "Configures two-way coupling frequency between two components.",
        "details": (
            "A common performance and convergence lever. In steady-state runs, overly frequent coupling can "
            "waste CPU time or destabilize relaxation; overly infrequent coupling can slow or distort convergence."
        ),
        "see_also": ["#CYCLE", "#TIMEACCURATE", "#COMPONENTMAP"],
        "aliases": ["COUPLE2", "DnCouple", "DtCouple", "two-way coupling"],
        "tags": ["coupling", "execution", "performance"],
    },
    "#SAVERESTART": {
        "title": "#SAVERESTART",
        "summary": "Controls whether restart data is saved and how often.",
        "details": (
            "Frequency is step-based in steady-state mode and time-based in time-accurate mode. "
            "Final restart data is still written when enabled. This is a common source of confusion in "
            "long production runs and restart strategy discussions."
        ),
        "see_also": ["#RESTARTOUTDIR", "#RESTARTFILE", "Restart.pl"],
        "aliases": ["SAVERESTART", "DoSaveRestart", "DnSaveRestart", "DtSaveRestart"],
        "tags": ["restart", "output", "time"],
    },
    "PARAM.XML": {
        "title": "PARAM.XML",
        "summary": "Authoritative definition of SWMF control-module commands and parameters.",
        "details": (
            "The main source of truth for command names, types, ranges, defaults, and requiredness for the "
            "framework-level parameter vocabulary. Curated knowledge should summarize it, not replace it."
        ),
        "see_also": ["component PARAM.XML", "Scripts/TestParam.pl", "ParamEditor.pl"],
        "aliases": ["main PARAM.XML", "top-level PARAM.XML", "control PARAM.XML"],
        "tags": ["authoritative", "schema", "param"],
    },
    "component PARAM.XML": {
        "title": "component PARAM.XML",
        "summary": "Authoritative definition of component-specific commands and parameters.",
        "details": (
            "Each component version owns its own PARAM.XML. MCP should consult this when a command is inside "
            "a #BEGIN_COMP block or when diagnosing component-only settings, defaults, ranges, or requirements."
        ),
        "see_also": ["PARAM.XML", "#BEGIN_COMP", "Scripts/TestParam.pl"],
        "aliases": ["GM/BATSRUS/PARAM.XML", "component xml", "BATSRUS PARAM.XML"],
        "tags": ["authoritative", "components", "schema"],
    },
    "Scripts/TestParam.pl": {
        "title": "Scripts/TestParam.pl",
        "summary": "Authoritative SWMF-side PARAM validation script.",
        "details": (
            "This is the preferred validator for real PARAM correctness because it uses the same XML-defined "
            "semantics that drive SWMF parameter interpretation. Use it after cheap preflight checks, and treat "
            "script launch/context failures separately from actual PARAM failures."
        ),
        "see_also": ["PARAM.XML", "component PARAM.XML", "ParamEditor.pl"],
        "aliases": ["TestParam.pl", "testparam", "param validator"],
        "tags": ["authoritative", "validation", "diagnostics"],
    },
    "share/Scripts/ParamEditor.pl": {
        "title": "share/Scripts/ParamEditor.pl",
        "summary": "Browser-based editor for constructing and checking PARAM.in files from PARAM.XML.",
        "details": (
            "Useful when the user wants an interactive way to build or inspect parameter files. It exposes "
            "manual/help text and correctness checks derived from PARAM.XML."
        ),
        "see_also": ["PARAM.XML", "Scripts/TestParam.pl"],
        "aliases": ["ParamEditor.pl", "param editor", "editor GUI"],
        "tags": ["workflow", "editor", "validation"],
    },
    "Config.pl": {
        "title": "Config.pl",
        "summary": "Primary SWMF configuration script for install/build/component-version selection.",
        "details": (
            "Owns installation, compiler selection, debug/optimization switches, and component version "
            "selection. It is build-time configuration, not run-time PARAM validation."
        ),
        "see_also": ["Scripts/Configure.pl", "#COMPONENTMAP"],
        "aliases": ["config", "config.pl", "install", "compiler", "-v", "-O", "-debug"],
        "tags": ["build", "install", "configuration"],
    },
    "Scripts/Configure.pl": {
        "title": "Scripts/Configure.pl",
        "summary": "Builds a reduced SWMF package containing only selected components.",
        "details": (
            "This is for source-package tailoring, not ordinary run setup. It removes component directories "
            "and references to them when constructing a smaller configured package."
        ),
        "see_also": ["Config.pl"],
        "aliases": ["Configure.pl", "configure script", "reduced package"],
        "tags": ["build", "packaging"],
    },
    "Restart.pl": {
        "title": "Restart.pl",
        "summary": "Collects, checks, and links restart trees for continued runs.",
        "details": (
            "Useful when a run must continue after failure, queue limits, or staged workflow. It gathers "
            "restart artifacts into a tree, links them back into a run directory, and checks consistency."
        ),
        "see_also": ["#SAVERESTART", "#RESTARTOUTDIR", "#RESTARTFILE"],
        "aliases": ["restart", "restart.pl", "restart tree"],
        "tags": ["restart", "workflow"],
    },
    "PostProc.pl": {
        "title": "PostProc.pl",
        "summary": "Post-processes run outputs and can organize results into a structured tree.",
        "details": (
            "Used after or during a run to collect per-processor outputs, transform them into more usable "
            "results, and optionally build an organized RESULTS tree."
        ),
        "see_also": ["read_data", "animate_data"],
        "aliases": ["postproc", "postproc.pl", "post processing"],
        "tags": ["workflow", "output", "results"],
    },
    "Scripts/Performance.pl": {
        "title": "Scripts/Performance.pl",
        "summary": "Performance-testing helper for trying layouts and configurations.",
        "details": (
            "Useful when layout/coupling tuning is the main goal rather than physics output. It complements "
            "stub-based testing and helps reason about efficient configurations."
        ),
        "see_also": ["#COMPONENTMAP", "#CYCLE", "#COUPLE2"],
        "aliases": ["Performance.pl", "performance"],
        "tags": ["performance", "layout", "testing"],
    },
    "Param/": {
        "title": "Param/",
        "summary": "Repository of example and template PARAM.in files.",
        "details": (
            "A major practical source of real run layouts and command combinations. In many real support "
            "flows, examples are the fastest way to suggest a plausible starting point before authoritative validation."
        ),
        "see_also": ["PARAM.XML", "Scripts/TestParam.pl"],
        "aliases": ["Param directory", "examples", "template PARAM.in"],
        "tags": ["examples", "templates", "workflow"],
    },
    "read_data": {
        "title": "read_data",
        "summary": "IDL macro to read SWMF snapshots into x and w arrays.",
        "details": (
            "The basic entry point for interactive data inspection. It reads file metadata and variables, and "
            "feeds subsequent plotting/analysis macros."
        ),
        "see_also": ["plot_data", "show_data", "animate_data"],
        "aliases": ["readdata", "read data"],
        "tags": ["idl", "visualization", "io"],
    },
    "plot_data": {
        "title": "plot_data",
        "summary": "IDL macro to plot functions of data already loaded into x and w.",
        "details": (
            "This is the main plotting workhorse after read_data. Function choice is controlled by func and "
            "rendering by plotmode."
        ),
        "see_also": ["read_data", "show_data", "func", "plotmode"],
        "aliases": ["plotdata", "plot data"],
        "tags": ["idl", "visualization", "plotting"],
    },
    "show_data": {
        "title": "show_data",
        "summary": "IDL convenience macro to read/re-read and immediately plot data.",
        "details": (
            "Useful for quick interactive inspection when the user does not want separate read and plot steps."
        ),
        "see_also": ["read_data", "plot_data"],
        "aliases": ["showdata", "show data"],
        "tags": ["idl", "visualization"],
    },
    "animate_data": {
        "title": "animate_data",
        "summary": "IDL macro for animation, time-series plotting, and multi-file comparison.",
        "details": (
            "Combines read-and-plot behavior for one or more snapshots/files. Useful for movies, comparisons, "
            "and repeated plotting over time."
        ),
        "see_also": ["read_data", "plot_data", "show_data"],
        "aliases": ["animatedata", "animate data"],
        "tags": ["idl", "visualization", "animation"],
    },
    "read_log_data": {
        "title": "read_log_data",
        "summary": "IDL macro to read SWMF log or satellite files into log arrays.",
        "details": (
            "Use when analyzing time-series quantities from .log or .sat files rather than snapshot plot files."
        ),
        "see_also": ["plot_log_data", "show_log_data"],
        "aliases": ["readlogdata", "read log data"],
        "tags": ["idl", "logs", "visualization"],
    },
    "plot_log_data": {
        "title": "plot_log_data",
        "summary": "IDL macro to visualize quantities already read from SWMF log files.",
        "details": (
            "Convenience layer above raw IDL plotting for log-derived time series."
        ),
        "see_also": ["read_log_data", "show_log_data"],
        "aliases": ["plotlogdata", "plot log data"],
        "tags": ["idl", "logs", "plotting"],
    },
    "func": {
        "title": "func",
        "summary": "IDL string parameter that selects plotted variables or expressions.",
        "details": (
            "Can reference raw variable names, predefined function names, or expressions. Vector-style pairs "
            "such as ux;uy or bx;bz are meaningful for vector/stream plotting modes."
        ),
        "see_also": ["plotmode", "plot_data", "funcdef"],
        "aliases": ["function string", "func string"],
        "tags": ["idl", "plotting"],
    },
    "plotmode": {
        "title": "plotmode",
        "summary": "IDL string parameter that selects how functions are rendered.",
        "details": (
            "Controls contour, filled contour, streamlines, vector plots, surfaces, and related modifiers. "
            "A very common support question is not 'how do I read data' but 'which plotmode should I use'."
        ),
        "see_also": ["func", "plot_data", "animate_data"],
        "aliases": ["plot mode", "plotmode string"],
        "tags": ["idl", "plotting"],
    },
}

def normalize_curated_lookup_key(name: str) -> str:
    raw = name.strip()
    if raw in CURATED_KNOWLEDGE:
        return raw

    if not raw.startswith("#"):
        hash_variant = f"#{raw.upper()}"
        if hash_variant in CURATED_KNOWLEDGE:
            return hash_variant

    lowered = raw.lower()
    for key, payload in CURATED_KNOWLEDGE.items():
        aliases = payload.get("aliases", [])
        if lowered == key.lower() or lowered in {item.lower() for item in aliases}:
            return key

    return raw
