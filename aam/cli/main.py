"""CLI entrypoint for Agent Asset Management."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from aam import __version__
from aam.cli import commands


def build_parser() -> argparse.ArgumentParser:
    """Build the Phase 1 CLI parser."""
    parser = argparse.ArgumentParser(
        prog="aam",
        description="Agent Asset Management command line interface.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"aam {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Create a package skeleton.")
    init_parser.add_argument("package_dir")
    init_parser.set_defaults(handler=commands.init_package)

    validate_parser = subparsers.add_parser("validate", help="Validate a package.")
    validate_parser.add_argument("package_dir")
    validate_parser.add_argument("--json", action="store_true")
    validate_parser.set_defaults(handler=commands.validate)

    index_parser = subparsers.add_parser("index", help="Build a temporary registry.")
    index_parser.add_argument("package_dir")
    index_parser.add_argument("--json", action="store_true")
    index_parser.set_defaults(handler=commands.index)

    list_parser = subparsers.add_parser("list", help="List registry objects.")
    list_subparsers = list_parser.add_subparsers(dest="list_command", required=True)
    list_assets_parser = list_subparsers.add_parser("assets", help="List assets.")
    list_assets_parser.add_argument("package_dir")
    list_assets_parser.add_argument("--type")
    list_assets_parser.add_argument("--tag")
    list_assets_parser.add_argument("--trust")
    list_assets_parser.add_argument("--lifecycle")
    list_assets_parser.add_argument("--target-host")
    list_assets_parser.add_argument("--json", action="store_true")
    list_assets_parser.set_defaults(handler=commands.list_assets)
    list_profiles_parser = list_subparsers.add_parser("profiles", help="List profiles.")
    list_profiles_parser.add_argument("package_dir")
    list_profiles_parser.add_argument("--json", action="store_true")
    list_profiles_parser.set_defaults(handler=commands.list_profiles)

    show_parser = subparsers.add_parser("show", help="Show registry objects.")
    show_subparsers = show_parser.add_subparsers(dest="show_command", required=True)
    show_asset_parser = show_subparsers.add_parser("asset", help="Show asset metadata.")
    show_asset_parser.add_argument("package_dir")
    show_asset_parser.add_argument("asset_id")
    show_asset_parser.add_argument("--json", action="store_true")
    show_asset_parser.set_defaults(handler=commands.show_asset)
    show_card_parser = show_subparsers.add_parser("card", help="Show an Asset Card.")
    show_card_parser.add_argument("package_dir")
    show_card_parser.add_argument("asset_id")
    show_card_parser.add_argument("--json", action="store_true")
    show_card_parser.set_defaults(handler=commands.show_card)

    graph_parser = subparsers.add_parser("graph", help="Graph commands.")
    graph_subparsers = graph_parser.add_subparsers(dest="graph_command", required=True)
    graph_export_parser = graph_subparsers.add_parser(
        "export",
        help="Export graph projection.",
    )
    graph_export_parser.add_argument("package_dir")
    graph_export_parser.add_argument("--json", action="store_true")
    graph_export_parser.set_defaults(handler=commands.graph_export)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Phase 1 CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0
    return handler(args)
