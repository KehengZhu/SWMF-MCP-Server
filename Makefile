# SWMF MCP Server – build/install helper
#
# Targets
#   cache-model   Install FastEmbed deps and warm the local embedding cache
#   preindex      Install FastEmbed deps and pre-index repos
#   prepare       Run all preparation steps except install
#   install       Write .mcp.json in TARGET_DIR and symlink the server there
#
# Optional flags (override on the command line, e.g. make preindex SWMF_ROOT=/path/to/SWMF)
#   SWMF_ROOT       Absolute or relative path to the SWMF source tree
#                   Default: $(REPO_DIR)/SWMF
#   SWMFSOLAR_ROOT  Absolute or relative path to the SWMFSOLAR source tree
#                   Default: $(REPO_DIR)/SWMFSOLAR
#   TARGET_DIR      Directory where the MCP server will be installed
#                   Default: $(REPO_DIR)

# ---------------------------------------------------------------------------
# Paths and defaults
# ---------------------------------------------------------------------------
REPO_DIR      := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
VENV          := $(REPO_DIR)/.venv
PYTHON        := $(VENV)/bin/python
PIP           := $(VENV)/bin/pip
SCRIPTS_DIR   := $(REPO_DIR)/scripts

SWMF_ROOT      ?= $(REPO_DIR)/SWMF
SWMFSOLAR_ROOT ?= $(REPO_DIR)/SWMFSOLAR
TARGET_DIR     ?= $(REPO_DIR)
SEMANTIC_EXTRA ?= $(shell if command -v nvidia-smi >/dev/null 2>&1; then echo semantic-gpu; else echo semantic; fi)

# Resolved absolute paths (handles relative inputs gracefully)
_SWMF_ABS      := $(abspath $(SWMF_ROOT))
_SWMFSOLAR_ABS := $(abspath $(SWMFSOLAR_ROOT))
_TARGET_ABS    := $(abspath $(TARGET_DIR))

# ---------------------------------------------------------------------------
# Phony targets
# ---------------------------------------------------------------------------
.PHONY: all prepare semantic-deps cache-model preindex install help

all: prepare

# ---------------------------------------------------------------------------
# prepare – run all setup steps except install
# ---------------------------------------------------------------------------
prepare: cache-model preindex

# ---------------------------------------------------------------------------
# semantic-deps – install FastEmbed dependencies once
# ---------------------------------------------------------------------------
semantic-deps: _check_venv
	@echo "==> Installing semantic extras ($(SEMANTIC_EXTRA))…"
	$(PIP) install --quiet "$(REPO_DIR)[$(SEMANTIC_EXTRA)]"

# ---------------------------------------------------------------------------
# cache-model – download/warm the local embedding model cache
# ---------------------------------------------------------------------------
cache-model: semantic-deps
	@echo "==> Caching embedding model locally…"
	$(PYTHON) "$(SCRIPTS_DIR)/cache_model.py"

# ---------------------------------------------------------------------------
# preindex – install FastEmbed deps and build the knowledge index
# ---------------------------------------------------------------------------
preindex: semantic-deps
	@echo "==> Pre-indexing SWMF root: $(_SWMF_ABS)"
	@test -d "$(_SWMF_ABS)" || (echo "ERROR: SWMF_ROOT '$(_SWMF_ABS)' does not exist." && exit 1)
	SWMF_ROOT="$(_SWMF_ABS)" SWMFSOLAR_ROOT="$(_SWMFSOLAR_ABS)" \
		$(PYTHON) "$(SCRIPTS_DIR)/preindex.py"

# ---------------------------------------------------------------------------
# install – write .mcp.json at TARGET_DIR and symlink/copy the repo there
# ---------------------------------------------------------------------------
install: _check_venv
	@echo "==> Installing MCP server into: $(_TARGET_ABS)"
	@mkdir -p "$(_TARGET_ABS)"
	@if [ "$(_TARGET_ABS)" != "$(REPO_DIR)" ]; then \
		ln -sfn "$(REPO_DIR)" "$(_TARGET_ABS)/.swmf_mcp_server"; \
		echo "    Symlinked $(REPO_DIR) -> $(_TARGET_ABS)/.swmf_mcp_server"; \
		SERVER_PYTHON="$(_TARGET_ABS)/.swmf_mcp_server/.venv/bin/python"; \
	else \
		SERVER_PYTHON="$(PYTHON)"; \
	fi; \
	SWMF_ROOT="$(_SWMF_ABS)" \
	SWMFSOLAR_ROOT="$(_SWMFSOLAR_ABS)" \
	TARGET_DIR="$(_TARGET_ABS)" \
	SERVER_PYTHON="$$SERVER_PYTHON" \
		$(PYTHON) "$(SCRIPTS_DIR)/install.py"

# ---------------------------------------------------------------------------
# Internal – verify the virtualenv exists before doing real work
# ---------------------------------------------------------------------------
_check_venv:
	@test -x "$(PYTHON)" || \
		(echo "ERROR: virtualenv not found at $(VENV). Run: python -m venv $(VENV) && $(PIP) install -e '$(REPO_DIR)[semantic]'" && exit 1)

# ---------------------------------------------------------------------------
# help
# ---------------------------------------------------------------------------
help:
	@echo ""
	@echo "SWMF MCP Server – Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  make                             Run cache-model, preindex, and future prep steps"
	@echo "  make cache-model                 Download/warm the local embedding model cache"
	@echo "  make preindex                    Build the knowledge index"
	@echo "  make prepare                     Run all preparation steps except install"
	@echo "  make install                     Write .mcp.json and symlink into TARGET_DIR"
	@echo ""
	@echo "Optional variables (pass on the command line):"
	@echo "  SWMF_ROOT=<path>       SWMF source tree   (default: $(REPO_DIR)/SWMF)"
	@echo "  SWMFSOLAR_ROOT=<path>  SWMFSOLAR tree     (default: $(REPO_DIR)/SWMFSOLAR)"
	@echo "  TARGET_DIR=<path>      Install destination (default: $(REPO_DIR))"
	@echo "  SEMANTIC_EXTRA=<name>  semantic or semantic-gpu (default auto-detect)"
	@echo "  SWMF_KNOWLEDGE_EMBEDDING_MODEL=<name-or-path>  Embedding model override"
	@echo ""
	@echo "Examples:"
	@echo "  make"
	@echo "  make cache-model"
	@echo "  make preindex"
	@echo "  make preindex SWMF_ROOT=/data/SWMF SWMFSOLAR_ROOT=/data/SWMFSOLAR"
	@echo "  make install TARGET_DIR=~/myrun SWMF_ROOT=/data/SWMF"
	@echo ""
