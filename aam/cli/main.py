"""Placeholder CLI entrypoint for Agent Asset Management."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from aam import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the placeholder parser for the Phase 1 CLI foundation."""
    parser = argparse.ArgumentParser(
        prog="aam",
        description="Agent Asset Management command line interface.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"aam {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the placeholder CLI."""
    parser = build_parser()
    parser.parse_args(argv)
    return 0
