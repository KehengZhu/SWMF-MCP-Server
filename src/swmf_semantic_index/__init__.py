"""
swmf_semantic_index
===================
Standalone local semantic index engine for SWMF and SWMFSOLAR source trees.

Provides corpus discovery, SWMF-aware chunking, local-only hybrid retrieval
(lexical + semantic), and a CLI for building and querying the index.

This package is independent of swmf_mcp_server. It does not import from the MCP
server and does not require the MCP server to be running. The MCP server may
optionally consume this package through a thin bridge adapter.

Public API surface:
  from swmf_semantic_index.retrieval import SemanticIndex
  from swmf_semantic_index.models import ChunkRecord, RetrievalResult, CorpusManifest
"""

__version__ = "0.1.0"
