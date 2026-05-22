"""CLI output formatting helpers."""

from __future__ import annotations

import json
from typing import Any

from aam.models.asset_card import AssetCardProjection
from aam.models.indexed import IndexedAsset, IndexedProfile, InMemoryRegistry
from aam.models.validation import ValidationIssue, ValidationReport


def emit_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def registry_summary(registry: InMemoryRegistry) -> dict[str, int]:
    return {
        "asset_count": len(registry.assets),
        "edge_count": len(registry.graph.edges),
        "node_count": len(registry.graph.nodes),
        "package_count": len(registry.packages),
        "profile_count": len(registry.profiles),
    }


def validation_payload(report: ValidationReport) -> dict[str, Any]:
    return {
        "ok": report.ok,
        "package_id": report.package_id,
        "issues": [_issue_payload(issue) for issue in report.issues],
    }


def asset_payload(
    asset: IndexedAsset,
    dependencies: list[IndexedAsset],
    reverse_dependencies: list[IndexedAsset],
) -> dict[str, Any]:
    return {
        "id": asset.id,
        "qualified_id": asset.qualified_id,
        "package_id": asset.package_id,
        "package_version": asset.package_version,
        "type": asset.type.value,
        "path": asset.path,
        "visibility": asset.visibility.value,
        "lifecycle_status": asset.lifecycle_status.value,
        "trust_status": asset.trust_status.value,
        "description": asset.description,
        "tags": list(asset.tags),
        "target_hosts": list(asset.target_hosts),
        "permissions": asset.permissions.model_dump(mode="json"),
        "context_cost": asset.context_cost.model_dump(mode="json"),
        "content_hash": asset.content_hash,
        "dependencies": [dependency.qualified_id for dependency in dependencies],
        "reverse_dependencies": [
            dependency.qualified_id for dependency in reverse_dependencies
        ],
    }


def asset_list_payload(assets: list[IndexedAsset]) -> dict[str, Any]:
    return {
        "assets": [
            {
                "id": asset.id,
                "qualified_id": asset.qualified_id,
                "type": asset.type.value,
                "trust_status": asset.trust_status.value,
                "lifecycle_status": asset.lifecycle_status.value,
                "tags": list(asset.tags),
                "target_hosts": list(asset.target_hosts),
            }
            for asset in assets
        ]
    }


def profile_list_payload(profiles: list[IndexedProfile]) -> dict[str, Any]:
    return {
        "profiles": [
            {
                "id": profile.id,
                "qualified_id": profile.qualified_id,
                "target_host": profile.target_host,
                "tags": list(profile.tags),
                "includes": list(profile.resolved_includes),
            }
            for profile in profiles
        ]
    }


def card_payload(card: AssetCardProjection) -> dict[str, Any]:
    return card.model_dump(mode="json")


def graph_payload(registry: InMemoryRegistry) -> dict[str, Any]:
    return registry.graph.model_dump(mode="json")


def print_validation_report(report: ValidationReport) -> None:
    status = "ok" if report.ok else "failed"
    print(f"Validation {status} for package {report.package_id or '<unknown>'}")
    for issue in report.issues:
        print(f"{issue.severity.value.upper()} {issue.code}: {issue.message}")


def _issue_payload(issue: ValidationIssue) -> dict[str, Any]:
    return issue.model_dump(mode="json")
