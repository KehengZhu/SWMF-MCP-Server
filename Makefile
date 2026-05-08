# SWMF AI – bootstrap/install helper
#
# Public targets
#   make          Bootstrap the Python MCP runtime and prepare the knowledge index
#   install       Write one agent-specific MCP config plus agent asset symlinks
#   clean         Remove generated Python/build/test artifacts
#
# Optional flags (override on the command line, e.g. make SWMF_ROOT=/path/to/SWMF)
#   SWMF_ROOT       Absolute or relative path to the SWMF source tree
#                   Default: $(REPO_DIR)/SWMF
#   SWMF_IDL_EXEC   Absolute path to the IDL executable
#                   Default: omitted unless passed
#   SWMFSOLAR_ROOT  Absolute or relative path to the SWMFSOLAR source tree
#                   Default: auto-detected during install only
#   AGENT           Agent surface to install
#                   Required for install: claude, copilot-vscode, copilot-cli, codex
#   TARGET_DIR      Directory where the MCP server will be installed
#                   Default: $(REPO_DIR)

# ---------------------------------------------------------------------------
# Paths and defaults
# ---------------------------------------------------------------------------
REPO_DIR      := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
VENV          := $(REPO_DIR)/.venv
PYTHON        := $(VENV)/bin/python
SCRIPTS_DIR   := $(REPO_DIR)/scripts
BOOTSTRAP_PYTHON ?= $(shell command -v python3 || command -v python)
UV_CACHE_DIR     ?= $(REPO_DIR)/.uv-cache

SWMF_ROOT      ?= $(REPO_DIR)/SWMF
SWMFSOLAR_ROOT ?=
SWMF_IDL_EXEC  ?=
AGENT          ?=
TARGET_DIR     ?= $(REPO_DIR)
SEMANTIC_EXTRA ?= $(shell if command -v nvidia-smi >/dev/null 2>&1; then echo semantic-gpu; else echo semantic; fi)

# Resolved absolute paths (handles relative inputs gracefully)
_SWMF_ABS       := $(abspath $(SWMF_ROOT))
_SWMFSOLAR_ABS  := $(if $(strip $(SWMFSOLAR_ROOT)),$(abspath $(SWMFSOLAR_ROOT)))
_SWMF_IDL_ABS   := $(if $(strip $(SWMF_IDL_EXEC)),$(abspath $(SWMF_IDL_EXEC)))
_TARGET_ABS     := $(abspath $(TARGET_DIR))

# ---------------------------------------------------------------------------
# Phony targets
# ---------------------------------------------------------------------------
.PHONY: all _bootstrap _prepare_runtime _semantic_deps _cache_model _preindex install clean help

all: _prepare_runtime

# ---------------------------------------------------------------------------
# _bootstrap – ensure uv exists, then reuse or create/sync the project virtualenv
# ---------------------------------------------------------------------------
_bootstrap:
	@test -n "$(strip $(BOOTSTRAP_PYTHON))" || (echo "ERROR: python3 or python is required to bootstrap uv." && exit 1)
	@mkdir -p "$(UV_CACHE_DIR)"
	@UV_BIN="$$(command -v uv 2>/dev/null || true)"; \
	if [ -z "$$UV_BIN" ]; then \
		echo "==> Installing uv via $(BOOTSTRAP_PYTHON) -m pip --user uv"; \
		"$(BOOTSTRAP_PYTHON)" -m pip install --user uv; \
		UV_BIN="$$(command -v uv 2>/dev/null || true)"; \
		if [ -z "$$UV_BIN" ]; then \
			USER_BASE="$$("$(BOOTSTRAP_PYTHON)" -c 'import site; print(site.USER_BASE)')"; \
			UV_BIN="$$USER_BASE/bin/uv"; \
		fi; \
	fi; \
	test -x "$$UV_BIN" || (echo "ERROR: uv installation succeeded but no executable was found." && exit 1); \
	echo "==> Using uv: $$UV_BIN"; \
	if [ -x "$(PYTHON)" ]; then \
		if UV_CACHE_DIR="$(UV_CACHE_DIR)" "$$UV_BIN" sync --directory "$(REPO_DIR)" --extra "$(SEMANTIC_EXTRA)" --check >/dev/null 2>&1; then \
			echo "==> Existing .venv is already synchronized; reusing $(VENV)"; \
			exit 0; \
		fi; \
		echo "==> Existing .venv is present but needs sync; updating in place"; \
	fi; \
	UV_CACHE_DIR="$(UV_CACHE_DIR)" "$$UV_BIN" venv "$(VENV)" --allow-existing; \
	UV_CACHE_DIR="$(UV_CACHE_DIR)" "$$UV_BIN" sync --directory "$(REPO_DIR)" --extra "$(SEMANTIC_EXTRA)"

# ---------------------------------------------------------------------------
# _prepare_runtime – run all local MCP preparation steps except install
# ---------------------------------------------------------------------------
_prepare_runtime: _cache_model _preindex

# ---------------------------------------------------------------------------
# _semantic_deps – ensure the runtime is ready for embedding/index operations
# ---------------------------------------------------------------------------
_semantic_deps: _bootstrap
	@echo "==> uv environment is ready with extras: $(SEMANTIC_EXTRA)"

# ---------------------------------------------------------------------------
# _cache_model – download/warm the local embedding model cache
# ---------------------------------------------------------------------------
_cache_model: _semantic_deps
	@echo "==> Caching embedding model locally…"
	$(PYTHON) "$(SCRIPTS_DIR)/cache_model.py"

# ---------------------------------------------------------------------------
# _preindex – build the knowledge index used by evidence search
# ---------------------------------------------------------------------------
_preindex: _semantic_deps
	@echo "==> Pre-indexing SWMF root: $(_SWMF_ABS)"
	@test -d "$(_SWMF_ABS)" || (echo "ERROR: SWMF_ROOT '$(_SWMF_ABS)' does not exist." && exit 1)
	SWMF_ROOT="$(_SWMF_ABS)" SWMFSOLAR_ROOT="$(_SWMFSOLAR_ABS)" \
		$(PYTHON) "$(SCRIPTS_DIR)/preindex.py"

# ---------------------------------------------------------------------------
# install – write one agent-specific install output into TARGET_DIR
# ---------------------------------------------------------------------------
install: _bootstrap
	@test -n "$(strip $(AGENT))" || (echo "ERROR: AGENT is required. Choose one of: claude, copilot-vscode, copilot-cli, codex" && exit 1)
	@echo "==> Installing MCP bundle into: $(_TARGET_ABS)"
	@mkdir -p "$(_TARGET_ABS)"
	@if [ "$(_TARGET_ABS)" != "$(REPO_DIR)" ]; then \
		ln -sfn "$(REPO_DIR)" "$(_TARGET_ABS)/.swmf_mcp_server"; \
		echo "    Symlinked $(REPO_DIR) -> $(_TARGET_ABS)/.swmf_mcp_server"; \
		SERVER_PYTHON="$(_TARGET_ABS)/.swmf_mcp_server/.venv/bin/python"; \
	else \
		SERVER_PYTHON="$(PYTHON)"; \
	fi; \
	AGENT="$(AGENT)" \
	SWMF_ROOT="$(_SWMF_ABS)" \
	SWMF_IDL_EXEC="$(_SWMF_IDL_ABS)" \
	SWMFSOLAR_ROOT="$(_SWMFSOLAR_ABS)" \
	TARGET_DIR="$(_TARGET_ABS)" \
	SERVER_PYTHON="$$SERVER_PYTHON" \
		$(PYTHON) "$(SCRIPTS_DIR)/install.py"

# ---------------------------------------------------------------------------
# clean – remove generated artifacts that can preserve stale interfaces
# ---------------------------------------------------------------------------
clean:
	@echo "==> Removing generated Python/build/test artifacts"
	@find "$(REPO_DIR)" -type d -name "__pycache__" -prune -exec rm -rf {} +
	@rm -rf \
		"$(REPO_DIR)/build" \
		"$(REPO_DIR)/.pytest_cache" \
		"$(REPO_DIR)/src/swmf_mcp_prototype.egg-info"

# help
# ---------------------------------------------------------------------------
help:
	@echo ""
	@echo "SWMF AI – Makefile"
	@echo ""
	@echo "Public targets:"
	@echo "  make                             Bootstrap uv/.venv, sync dependencies, warm the embedding cache, and build the knowledge index"
	@echo "  make install                     Bootstrap uv/.venv if needed, then write one agent-specific install bundle into TARGET_DIR"
	@echo "  make clean                       Remove generated Python/build/test artifacts"
	@echo ""
	@echo "Install variables:"
	@echo "  AGENT=<name>          Required for make install. Supported: claude, copilot-vscode, copilot-cli, codex"
	@echo "  SWMF_ROOT=<path>       Required in generated configs. Default install input: $(REPO_DIR)/SWMF"
	@echo "  SWMF_IDL_EXEC=<path>   Optional. Written only when passed to make install."
	@echo "  SWMFSOLAR_ROOT=<path>  Optional override. Written only when the resolved path exists."
	@echo "  TARGET_DIR=<path>      Install destination. Default: $(REPO_DIR)"
	@echo ""
	@echo "SWMFSOLAR_ROOT auto-detect order for make install when no explicit path is passed:"
	@echo "  1. Sibling of the chosen SWMF_ROOT"
	@echo "  2. $(REPO_DIR)/SWMFSOLAR"
	@echo "  3. TARGET_DIR/SWMFSOLAR"
	@echo "  Only the first existing path is written."
	@echo ""
	@echo "Other optional variables:"
	@echo "  SEMANTIC_EXTRA=<name>  semantic or semantic-gpu (default auto-detect)"
	@echo "  BOOTSTRAP_PYTHON=<path>  Python used to install uv when uv is missing"
	@echo "  UV_CACHE_DIR=<path>  Writable cache dir for uv. Default: $(UV_CACHE_DIR)"
	@echo "  SWMF_KNOWLEDGE_EMBEDDING_MODEL=<name-or-path>  Embedding model override"
	@echo ""
	@echo "make install writes exactly one config surface plus symlinks for instructions and skills:"
	@echo "  AGENT=claude          TARGET_DIR/.mcp.json + TARGET_DIR/CLAUDE.md -> src/agent_assets/SWMF_CORE_DISCIPLINE.md + TARGET_DIR/.claude/skills -> src/agent_assets/skills"
	@echo "  AGENT=copilot-vscode  TARGET_DIR/.vscode/mcp.json + TARGET_DIR/.github/copilot-instructions.md -> src/agent_assets/SWMF_CORE_DISCIPLINE.md + TARGET_DIR/.github/skills -> src/agent_assets/skills"
	@echo "  AGENT=copilot-cli     TARGET_DIR/.mcp.json + TARGET_DIR/.github/copilot-instructions.md -> src/agent_assets/SWMF_CORE_DISCIPLINE.md + TARGET_DIR/.github/skills -> src/agent_assets/skills"
	@echo "  AGENT=codex           TARGET_DIR/.codex/config.toml + TARGET_DIR/AGENTS.md -> src/agent_assets/SWMF_CORE_DISCIPLINE.md + TARGET_DIR/.codex/skills -> src/agent_assets/skills"
	@echo "  External TARGET_DIR also gets: TARGET_DIR/.swmf_mcp_server -> $(REPO_DIR)"
	@echo ""
	@echo "Agent compatibility:"
	@echo "  Claude Code             .mcp.json + CLAUDE.md -> src/agent_assets/SWMF_CORE_DISCIPLINE.md + .claude/skills"
	@echo "  Copilot Chat / VS Code  .vscode/mcp.json + .github/copilot-instructions.md -> src/agent_assets/SWMF_CORE_DISCIPLINE.md + .github/skills"
	@echo "  Copilot CLI             .mcp.json + .github/copilot-instructions.md -> src/agent_assets/SWMF_CORE_DISCIPLINE.md + .github/skills"
	@echo "  Codex CLI               .codex/config.toml + AGENTS.md -> src/agent_assets/SWMF_CORE_DISCIPLINE.md + .codex/skills"
	@echo ""
	@echo "Examples:"
	@echo "  make"
	@echo "  make install AGENT=claude"
	@echo "  make install AGENT=copilot-vscode SWMF_ROOT=/path/to/SWMF"
	@echo "  make install AGENT=codex SWMF_ROOT=/path/to/SWMF SWMF_IDL_EXEC=/path/to/idl"
	@echo "  make install AGENT=copilot-cli SWMF_ROOT=/path/to/SWMF SWMFSOLAR_ROOT=/path/to/SWMFSOLAR"
	@echo "  make install AGENT=claude TARGET_DIR=/path/to/workspace SWMF_ROOT=/path/to/SWMF"
	@echo "  make clean"
	@echo ""
