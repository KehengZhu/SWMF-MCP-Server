"""
CLI entry point for the SWMF semantic index.

Commands:
  swmf-index build   --corpus PATH [--corpus PATH] [--cache DIR]
  swmf-index refresh --corpus PATH [--corpus PATH] [--cache DIR]
  swmf-index query   QUERY [--component C] [--top-k N] [--cache DIR]
  swmf-index status  [--cache DIR]
  swmf-index inspect CHUNK_ID [--cache DIR]

All commands write JSON to stdout for easy piping into other tools.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .models import CorpusSlice
from .retrieval import SemanticIndex


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_roots(corpus_paths: list[str]) -> list[tuple[Path, CorpusSlice]]:
    """
    Map each corpus path to a (path, CorpusSlice) pair.
    Heuristic: paths ending in 'SWMFSOLAR' or containing 'solar' (case-insensitive)
    are classified as SWMFSOLAR_SOURCE; everything else as SWMF_SOURCE.
    """
    roots = []
    for p in corpus_paths:
        path = Path(p).resolve()
        name = path.name.lower()
        if "solar" in name:
            slice_ = CorpusSlice.SWMFSOLAR_SOURCE
        else:
            slice_ = CorpusSlice.SWMF_SOURCE
        roots.append((path, slice_))
    return roots


def _print_json(obj) -> None:
    print(json.dumps(obj, indent=2, default=str))


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def cmd_build(args: argparse.Namespace) -> int:
    idx = SemanticIndex(cache_dir=Path(args.cache) if args.cache else None)
    try:
        roots = _resolve_roots(args.corpus)
        if not roots:
            print(json.dumps({"error": "no --corpus paths provided"}), file=sys.stderr)
            return 1

        print(f"Building index over {len(roots)} root(s)...", file=sys.stderr)
        manifest = idx.build(roots, incremental=False)
        _print_json({
            "status": "built",
            "built_at": manifest.built_at.isoformat() if manifest.built_at else None,
            "total_chunks": manifest.total_chunks,
            "total_files": manifest.total_files,
            "index_path": manifest.index_path,
            "roots": [
                {
                    "path": r.abs_path,
                    "slice": r.corpus_slice.value,
                    "files": r.file_count,
                    "chunks": r.chunk_count,
                }
                for r in manifest.roots
            ],
        })
        return 0
    finally:
        idx.close()


def cmd_refresh(args: argparse.Namespace) -> int:
    idx = SemanticIndex(cache_dir=Path(args.cache) if args.cache else None)
    try:
        roots = _resolve_roots(args.corpus)
        if not roots:
            print(json.dumps({"error": "no --corpus paths provided"}), file=sys.stderr)
            return 1

        print(f"Refreshing index (incremental) over {len(roots)} root(s)...", file=sys.stderr)
        manifest = idx.build(roots, incremental=True)
        _print_json({
            "status": "refreshed",
            "built_at": manifest.built_at.isoformat() if manifest.built_at else None,
            "total_chunks": manifest.total_chunks,
            "total_files": manifest.total_files,
            "index_path": manifest.index_path,
        })
        return 0
    finally:
        idx.close()


def cmd_query(args: argparse.Namespace) -> int:
    idx = SemanticIndex(cache_dir=Path(args.cache) if args.cache else None)
    try:
        results = idx.search(
            args.query,
            component=args.component,
            symbol=args.symbol,
            top_k=args.top_k,
        )
        _print_json({
            "query": args.query,
            "component_filter": args.component,
            "symbol_filter": args.symbol,
            "top_k": args.top_k,
            "result_count": len(results),
            "results": [
                {
                    "rank": r.rank,
                    "chunk_id": r.chunk.chunk_id,
                    "location": r.chunk.location,
                    "kind": r.chunk.kind.value,
                    "component": r.chunk.component,
                    "symbol": r.chunk.symbol,
                    "authority": r.authority_label,
                    "score": round(r.scores.combined, 4),
                    "score_breakdown": {
                        "lexical": round(r.scores.lexical_score, 4),
                        "component_match": round(r.scores.component_match, 4),
                        "symbol_match": round(r.scores.symbol_match, 4),
                    },
                    "excerpt": r.chunk.text[:400],
                }
                for r in results
            ],
        })
        return 0
    finally:
        idx.close()


def cmd_status(args: argparse.Namespace) -> int:
    idx = SemanticIndex(cache_dir=Path(args.cache) if args.cache else None)
    try:
        _print_json(idx.get_status())
        return 0
    finally:
        idx.close()


def cmd_inspect(args: argparse.Namespace) -> int:
    idx = SemanticIndex(cache_dir=Path(args.cache) if args.cache else None)
    try:
        idx._ensure_open()
        chunk = idx._store.get_chunk(args.chunk_id)
        if chunk is None:
            _print_json({"error": f"chunk not found: {args.chunk_id}"})
            return 1
        _print_json({
            "chunk_id": chunk.chunk_id,
            "location": chunk.location,
            "kind": chunk.kind.value,
            "authority": chunk.authority.name,
            "corpus_slice": chunk.corpus_slice.value,
            "component": chunk.component,
            "symbol": chunk.symbol,
            "parent_symbol": chunk.parent_symbol,
            "keywords": chunk.keywords,
            "text": chunk.text,
        })
        return 0
    finally:
        idx.close()


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swmf-index",
        description="SWMF semantic index — build, refresh, query, inspect.",
    )
    parser.add_argument(
        "--cache", metavar="DIR",
        help="Cache directory (default: .swmf_semantic_cache in cwd)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # build
    p_build = sub.add_parser("build", help="Build the index from scratch.")
    p_build.add_argument("--corpus", metavar="PATH", action="append", default=[],
                         help="Corpus root path (repeat for multiple roots).")

    # refresh
    p_refresh = sub.add_parser("refresh", help="Incrementally refresh the index.")
    p_refresh.add_argument("--corpus", metavar="PATH", action="append", default=[],
                            help="Corpus root path.")

    # query
    p_query = sub.add_parser("query", help="Search the index.")
    p_query.add_argument("query", help="Search query string.")
    p_query.add_argument("--component", metavar="NAME", help="Filter by component (GM, IE, ...).")
    p_query.add_argument("--symbol", metavar="NAME", help="Boost results matching symbol name.")
    p_query.add_argument("--top-k", type=int, default=10, dest="top_k",
                          help="Number of results to return.")

    # status
    sub.add_parser("status", help="Show index status.")

    # inspect
    p_inspect = sub.add_parser("inspect", help="Show full content of a specific chunk.")
    p_inspect.add_argument("chunk_id", help="Chunk ID to inspect.")

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "build": cmd_build,
        "refresh": cmd_refresh,
        "query": cmd_query,
        "status": cmd_status,
        "inspect": cmd_inspect,
    }
    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    sys.exit(handler(args))


if __name__ == "__main__":
    main()
