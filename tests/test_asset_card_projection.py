"""Tests for Phase 1 Asset Card projection behavior."""

from __future__ import annotations

import pytest

from aam.asset_card.projection import build_asset_card_projection
from aam.core.enums import (
    FilesystemPermission,
    LifecycleStatus,
    NetworkPermission,
    RiskLevel,
    ShellPermission,
    TrustStatus,
)
from aam.models.manifest import (
    AssetCardManifest,
    AssetManifest,
    ContextCostSpec,
    PackageInfo,
    PackageManifest,
    PermissionSpec,
    ProfileManifest,
    SourceProvenance,
)


def _manifest(asset: AssetManifest) -> PackageManifest:
    return PackageManifest(
        package=PackageInfo(
            id="local.assets",
            name="Local Assets",
            version="0.1.0",
            source=SourceProvenance(kind="manual_created"),
        ),
        assets=[
            asset,
            AssetManifest(
                id="style-guide",
                type="instruction",
                path="instructions/style.md",
                trust_status=TrustStatus.TRUSTED,
            ),
        ],
        profiles=[ProfileManifest(id="review", target_host="codex")],
    )


def test_asset_card_uses_manifest_card_title_and_summary() -> None:
    asset = AssetManifest(
        id="reviewer",
        type="agent",
        path="agents/reviewer.md",
        description="Asset description.",
        trust_status=TrustStatus.TRUSTED,
        agent_card=AssetCardManifest(
            title="Code Reviewer",
            summary="Reviews code.",
            intended_use=["review diffs"],
            input_context={"expects": ["diff"]},
            output_capabilities=["review comments"],
            risk_level=RiskLevel.LOW,
        ),
    )

    card = build_asset_card_projection(
        manifest=_manifest(asset),
        asset=asset,
        content_hash="sha256:abc",
    )

    assert card.title == "Code Reviewer"
    assert card.summary == "Reviews code."
    assert card.intended_use == ["review diffs"]
    assert card.input_context == {"expects": ["diff"]}
    assert card.output_capabilities == ["review comments"]
    assert card.risk_level is RiskLevel.LOW


def test_asset_card_falls_back_to_asset_id_and_description() -> None:
    asset = AssetManifest(
        id="reviewer",
        type="agent",
        path="agents/reviewer.md",
        description="Fallback description.",
        trust_status=TrustStatus.TRUSTED,
    )

    card = build_asset_card_projection(
        manifest=_manifest(asset),
        asset=asset,
        content_hash="sha256:abc",
    )

    assert card.title == "reviewer"
    assert card.summary == "Fallback description."


def test_asset_card_summary_falls_back_to_none_when_missing() -> None:
    asset = AssetManifest(
        id="reviewer",
        type="agent",
        path="agents/reviewer.md",
        trust_status=TrustStatus.TRUSTED,
    )

    card = build_asset_card_projection(
        manifest=_manifest(asset),
        asset=asset,
        content_hash="sha256:abc",
    )

    assert card.summary is None


def test_asset_card_preserves_trust_permissions_and_status_fields() -> None:
    permissions = PermissionSpec(
        filesystem=FilesystemPermission.BROAD,
        network=NetworkPermission.READ,
        shell=ShellPermission.LIMITED,
    )
    asset = AssetManifest(
        id="reviewer",
        type="agent",
        path="agents/reviewer.md",
        visibility="exported",
        lifecycle_status=LifecycleStatus.ACTIVE,
        trust_status=TrustStatus.BLOCKED,
        tags=["review", "agent"],
        target_hosts=["codex"],
        permissions=permissions,
        context_cost=ContextCostSpec(estimated_tokens=1200),
    )

    card = build_asset_card_projection(
        manifest=_manifest(asset),
        asset=asset,
        content_hash="sha256:abc",
    )

    assert card.trust_status is TrustStatus.BLOCKED
    assert card.permissions == permissions
    assert card.lifecycle_status is LifecycleStatus.ACTIVE
    assert card.visibility.value == "exported"
    assert card.tags == ["review", "agent"]
    assert card.target_hosts == ["codex"]
    assert card.estimated_context_cost == 1200


def test_asset_card_projects_resolved_dependencies_in_manifest_order() -> None:
    asset = AssetManifest(
        id="reviewer",
        type="agent",
        path="agents/reviewer.md",
        trust_status=TrustStatus.TRUSTED,
        depends_on=["asset:style-guide", "style-guide"],
    )

    card = build_asset_card_projection(
        manifest=_manifest(asset),
        asset=asset,
        content_hash="sha256:abc",
    )

    assert card.dependencies == [
        "local.assets:style-guide@0.1.0",
        "local.assets:style-guide@0.1.0",
    ]


def test_asset_card_raises_on_unresolvable_dependency() -> None:
    asset = AssetManifest(
        id="reviewer",
        type="agent",
        path="agents/reviewer.md",
        trust_status=TrustStatus.TRUSTED,
        depends_on=["asset:missing"],
    )

    with pytest.raises(ValueError, match="Unable to resolve dependency reference"):
        build_asset_card_projection(
            manifest=_manifest(asset),
            asset=asset,
            content_hash="sha256:abc",
        )


def test_asset_card_contains_all_phase_1_hard_fields() -> None:
    asset = AssetManifest(
        id="reviewer",
        type="agent",
        path="agents/reviewer.md",
        trust_status=TrustStatus.TRUSTED,
    )

    card = build_asset_card_projection(
        manifest=_manifest(asset),
        asset=asset,
        content_hash="sha256:abc",
    )

    assert set(card.model_dump().keys()) == {
        "id",
        "package_id",
        "version",
        "type",
        "title",
        "summary",
        "intended_use",
        "input_context",
        "output_capabilities",
        "tags",
        "target_hosts",
        "dependencies",
        "trust_status",
        "lifecycle_status",
        "visibility",
        "permissions",
        "risk_level",
        "estimated_context_cost",
        "content_hash",
        "source",
    }
