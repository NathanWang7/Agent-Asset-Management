"""Tests for Phase 1 manifest enums and typed models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from aam.core.enums import (
    AssetType,
    AssetVisibility,
    FilesystemPermission,
    GraphEdgeType,
    GraphNodeType,
    LifecycleStatus,
    NetworkPermission,
    RiskLevel,
    ShellPermission,
    SourceKind,
    TrustStatus,
    ValidationSeverity,
)
from aam.models.manifest import (
    AssetCardManifest,
    AssetManifest,
    PackageInfo,
    PackageManifest,
    PermissionSpec,
    ProfileManifest,
    SourceProvenance,
)


def test_core_enum_values_match_phase_1_manifest_contract() -> None:
    assert {member.value for member in AssetType} == {
        "prompt",
        "agent",
        "skill",
        "tool",
        "mcp_server",
        "workflow",
        "instruction",
        "knowledge",
        "eval_case",
        "template",
        "schema",
        "host_instruction_pack",
        "other",
    }
    assert {member.value for member in AssetVisibility} == {
        "internal",
        "exported",
        "shared",
    }
    assert {member.value for member in LifecycleStatus} == {
        "draft",
        "active",
        "deprecated",
        "archived",
    }
    assert {member.value for member in TrustStatus} == {
        "trusted",
        "unreviewed",
        "sandbox_only",
        "blocked",
        "needs_manual_review",
    }
    assert {member.value for member in FilesystemPermission} == {
        "none",
        "read",
        "write",
        "broad",
    }
    assert {member.value for member in NetworkPermission} == {
        "none",
        "read",
        "broad",
    }
    assert {member.value for member in ShellPermission} == {
        "none",
        "limited",
        "broad",
    }
    assert {member.value for member in RiskLevel} == {
        "low",
        "medium",
        "high",
        "unknown",
    }
    assert {member.value for member in SourceKind} == {
        "manual_created",
        "local_directory",
        "github_repository",
        "unknown",
    }
    assert {member.value for member in GraphNodeType} == {
        "package",
        "asset",
        "profile",
        "tag",
        "target_host",
        "source",
        "trust_status",
        "lifecycle_status",
    }
    assert {member.value for member in GraphEdgeType} == {
        "package_contains_asset",
        "package_contains_profile",
        "profile_includes_asset",
        "asset_depends_on_asset",
        "asset_has_tag",
        "profile_has_tag",
        "asset_targets_host",
        "asset_imported_from_source",
        "asset_has_trust_status",
        "asset_has_lifecycle_status",
    }
    assert {member.value for member in ValidationSeverity} == {
        "error",
        "warning",
        "info",
    }


def test_valid_asset_manifest_constructs_from_manifest_dict() -> None:
    asset = AssetManifest.model_validate(
        {
            "id": "prompt.greeting",
            "type": "prompt",
            "path": "prompts/greeting.md",
            "visibility": "shared",
            "lifecycle_status": "active",
            "trust_status": "trusted",
            "description": "Greeting prompt",
            "tags": ["prompt", "greeting"],
            "depends_on": ["asset:skill.formatter"],
            "target_hosts": ["codex"],
            "permissions": {
                "filesystem": "read",
                "network": "none",
                "shell": "limited",
            },
            "context_cost": {"estimated_tokens": 120},
            "agent_card": {
                "title": "Greeting Prompt",
                "summary": "Creates concise greetings.",
                "intended_use": ["Draft greetings"],
                "input_context": {"requires": ["recipient"]},
                "output_capabilities": ["greeting_text"],
                "risk_level": "low",
            },
            "metadata": {"owner": "local"},
        }
    )

    assert asset.type is AssetType.PROMPT
    assert asset.visibility is AssetVisibility.SHARED
    assert asset.lifecycle_status is LifecycleStatus.ACTIVE
    assert asset.trust_status is TrustStatus.TRUSTED
    assert asset.permissions.filesystem is FilesystemPermission.READ
    assert asset.permissions.network is NetworkPermission.NONE
    assert asset.permissions.shell is ShellPermission.LIMITED
    assert asset.agent_card.risk_level is RiskLevel.LOW


def test_manifest_defaults_are_safe_and_deterministic() -> None:
    asset = AssetManifest.model_validate(
        {
            "id": "skill.formatter",
            "type": "skill",
            "path": "skills/formatter.md",
        }
    )

    assert asset.visibility is AssetVisibility.INTERNAL
    assert asset.lifecycle_status is LifecycleStatus.DRAFT
    assert asset.trust_status is TrustStatus.UNREVIEWED
    assert asset.permissions == PermissionSpec()
    assert asset.permissions.filesystem is FilesystemPermission.NONE
    assert asset.permissions.network is NetworkPermission.NONE
    assert asset.permissions.shell is ShellPermission.NONE
    assert asset.agent_card == AssetCardManifest()
    assert asset.agent_card.risk_level is RiskLevel.UNKNOWN
    assert asset.tags == []
    assert asset.depends_on == []
    assert asset.target_hosts == []
    assert asset.metadata == {}


def test_default_factories_do_not_share_mutable_values() -> None:
    first = AssetManifest.model_validate(
        {"id": "prompt.first", "type": "prompt", "path": "prompts/first.md"}
    )
    second = AssetManifest.model_validate(
        {"id": "prompt.second", "type": "prompt", "path": "prompts/second.md"}
    )

    first.tags.append("changed")
    first.agent_card.input_context["key"] = "value"

    assert second.tags == []
    assert second.agent_card.input_context == {}


def test_invalid_enum_value_fails_deterministically() -> None:
    with pytest.raises(ValidationError) as error:
        AssetManifest.model_validate(
            {
                "id": "prompt.bad",
                "type": "not-an-asset-type",
                "path": "prompts/bad.md",
            }
        )

    assert "not-an-asset-type" in str(error.value)
    assert "prompt" in str(error.value)


def test_nested_manifest_construction() -> None:
    manifest = PackageManifest(
        package=PackageInfo(
            id="local.example",
            name="Local Example",
            version="0.1.0",
            source=SourceProvenance(
                kind=SourceKind.MANUAL_CREATED,
                original_location="/tmp/local-example",
            ),
        ),
        assets=[
            AssetManifest(
                id="instruction.review",
                type=AssetType.INSTRUCTION,
                path="instructions/review.md",
                tags=["review"],
                agent_card=AssetCardManifest(
                    title="Review Instruction",
                    intended_use=["Code review"],
                    output_capabilities=["review_findings"],
                    risk_level=RiskLevel.MEDIUM,
                ),
            )
        ],
        profiles=[
            ProfileManifest(
                id="codex-review",
                target_host="codex",
                includes=["asset:instruction.review"],
                tags=["review"],
            )
        ],
    )

    assert manifest.package.source.kind is SourceKind.MANUAL_CREATED
    assert manifest.assets[0].type is AssetType.INSTRUCTION
    assert manifest.profiles[0].includes == ["asset:instruction.review"]


def test_minimal_package_manifest_construction() -> None:
    manifest = PackageManifest.model_validate(
        {
            "package": {
                "id": "local.minimal",
                "name": "Local Minimal",
                "version": "0.1.0",
            }
        }
    )

    assert manifest.package.id == "local.minimal"
    assert manifest.package.source.kind is SourceKind.UNKNOWN
    assert manifest.assets == []
    assert manifest.profiles == []
