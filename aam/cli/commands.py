"""CLI command implementations for Phase 1."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

from aam.cli.formatters import (
    asset_list_payload,
    asset_payload,
    card_payload,
    emit_json,
    graph_payload,
    print_validation_report,
    profile_list_payload,
    registry_summary,
    validation_payload,
)
from aam.manifest.parser import ManifestParseError, parse_manifest
from aam.manifest.validator import validate_package
from aam.registry.builder import RegistryBuildError
from aam.registry.query import AssetFilters
from aam.registry.service import RegistryLookupError, RegistryService


def init_package(args: Namespace) -> int:
    package_root = Path(args.package_dir)
    package_root.mkdir(parents=True, exist_ok=True)
    manifest_path = package_root / "package.yaml"
    if manifest_path.exists():
        print(f"package.yaml already exists at {manifest_path}")
        return 1

    for directory in ("assets", "profiles", "agents", "instructions", "prompts"):
        (package_root / directory).mkdir(exist_ok=True)
    manifest_path.write_text(_minimal_manifest(package_root.name), encoding="utf-8")
    print(f"Initialized package at {package_root}")
    return 0


def validate(args: Namespace) -> int:
    try:
        package_root = Path(args.package_dir)
        manifest = parse_manifest(package_root)
        report = validate_package(package_root, manifest)
    except ManifestParseError as exc:
        _print_error(exc, json_output=args.json)
        return 1

    if args.json:
        emit_json(validation_payload(report))
    else:
        print_validation_report(report)
    return 0 if report.ok else 1


def index(args: Namespace) -> int:
    try:
        service = RegistryService.from_package_root(args.package_dir)
    except (ManifestParseError, RegistryBuildError) as exc:
        _print_build_error(exc, json_output=args.json)
        return 1

    summary = registry_summary(service.registry)
    if args.json:
        emit_json(summary)
    else:
        print(
            "Indexed "
            f"{summary['package_count']} package(s), "
            f"{summary['asset_count']} asset(s), "
            f"{summary['profile_count']} profile(s)"
        )
    return 0


def list_assets(args: Namespace) -> int:
    try:
        service = RegistryService.from_package_root(args.package_dir)
        filters = AssetFilters(
            type=args.type,
            tag=args.tag,
            trust_status=args.trust,
            lifecycle_status=args.lifecycle,
            target_host=args.target_host,
        )
        assets = service.list_assets(filters)
    except (ManifestParseError, RegistryBuildError) as exc:
        _print_build_error(exc, json_output=args.json)
        return 1

    if args.json:
        emit_json(asset_list_payload(assets))
    else:
        for asset in assets:
            print(f"{asset.id}\t{asset.type.value}\t{asset.trust_status.value}")
    return 0


def list_profiles(args: Namespace) -> int:
    try:
        service = RegistryService.from_package_root(args.package_dir)
        profiles = service.list_profiles()
    except (ManifestParseError, RegistryBuildError) as exc:
        _print_build_error(exc, json_output=args.json)
        return 1

    if args.json:
        emit_json(profile_list_payload(profiles))
    else:
        for profile in profiles:
            print(f"{profile.id}\t{profile.target_host}")
    return 0


def show_asset(args: Namespace) -> int:
    try:
        service = RegistryService.from_package_root(args.package_dir)
        asset = service.get_asset(args.asset_id)
        dependencies = service.get_dependencies(args.asset_id)
        reverse_dependencies = service.get_reverse_dependencies(args.asset_id)
    except (ManifestParseError, RegistryBuildError, RegistryLookupError) as exc:
        _print_command_error(exc, json_output=args.json)
        return 1

    payload = asset_payload(asset, dependencies, reverse_dependencies)
    if args.json:
        emit_json(payload)
    else:
        print(f"{payload['id']} ({payload['type']})")
        print(f"content_hash: {payload['content_hash']}")
        print(f"dependencies: {len(payload['dependencies'])}")
        print(f"reverse_dependencies: {len(payload['reverse_dependencies'])}")
    return 0


def show_card(args: Namespace) -> int:
    try:
        service = RegistryService.from_package_root(args.package_dir)
        card = service.get_asset_card(args.asset_id)
    except (ManifestParseError, RegistryBuildError, RegistryLookupError) as exc:
        _print_command_error(exc, json_output=args.json)
        return 1

    if args.json:
        emit_json(card_payload(card))
    else:
        print(f"{card.id}: {card.title}")
        if card.summary:
            print(card.summary)
    return 0


def graph_export(args: Namespace) -> int:
    try:
        service = RegistryService.from_package_root(args.package_dir)
    except (ManifestParseError, RegistryBuildError) as exc:
        _print_build_error(exc, json_output=args.json)
        return 1

    if args.json:
        emit_json(graph_payload(service.registry))
    else:
        graph = service.registry.graph
        print(f"Graph: {len(graph.nodes)} node(s), {len(graph.edges)} edge(s)")
    return 0


def _print_build_error(exc: Exception, *, json_output: bool) -> None:
    if isinstance(exc, RegistryBuildError):
        if json_output:
            emit_json(
                {
                    "ok": False,
                    "error": str(exc),
                    "validation": validation_payload(exc.validation_report),
                }
            )
            return
        print_validation_report(exc.validation_report)
        return
    _print_error(exc, json_output=json_output)


def _print_command_error(exc: Exception, *, json_output: bool) -> None:
    if isinstance(exc, RegistryBuildError):
        _print_build_error(exc, json_output=json_output)
        return
    _print_error(exc, json_output=json_output)


def _print_error(exc: Exception, *, json_output: bool) -> None:
    if json_output:
        emit_json({"ok": False, "error": str(exc)})
        return
    print(str(exc))


def _minimal_manifest(package_name: str) -> str:
    package_id = package_name.replace("_", "-")
    return (
        "package:\n"
        f"  id: {package_id}\n"
        f"  name: {package_name}\n"
        "  version: 0.1.0\n"
        "\n"
        "assets: []\n"
        "profiles: []\n"
    )
