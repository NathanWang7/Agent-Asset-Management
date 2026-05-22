"""Typed models for Phase 1 package manifests."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from aam.core.enums import (
    AssetType,
    AssetVisibility,
    FilesystemPermission,
    LifecycleStatus,
    NetworkPermission,
    RiskLevel,
    ShellPermission,
    SourceKind,
    TrustStatus,
)


class ManifestModel(BaseModel):
    """Base model for manifest schema objects."""

    model_config = ConfigDict(extra="forbid")


class SourceProvenance(ManifestModel):
    kind: SourceKind = SourceKind.UNKNOWN
    original_location: str | None = None
    resolved_ref: str | None = None

    @classmethod
    def unknown(cls) -> SourceProvenance:
        return cls()


class PermissionSpec(ManifestModel):
    filesystem: FilesystemPermission = FilesystemPermission.NONE
    network: NetworkPermission = NetworkPermission.NONE
    shell: ShellPermission = ShellPermission.NONE

    @classmethod
    def default(cls) -> PermissionSpec:
        return cls()


class ContextCostSpec(ManifestModel):
    estimated_tokens: int | None = None


class AssetCardManifest(ManifestModel):
    title: str | None = None
    summary: str | None = None
    intended_use: list[str] = Field(default_factory=list)
    input_context: dict[str, Any] = Field(default_factory=dict)
    output_capabilities: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.UNKNOWN


class PackageInfo(ManifestModel):
    id: str
    name: str
    version: str
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    source: SourceProvenance = Field(default_factory=SourceProvenance.unknown)


class AssetManifest(ManifestModel):
    id: str
    type: AssetType
    path: str
    visibility: AssetVisibility = AssetVisibility.INTERNAL
    lifecycle_status: LifecycleStatus = LifecycleStatus.DRAFT
    trust_status: TrustStatus = TrustStatus.UNREVIEWED
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    target_hosts: list[str] = Field(default_factory=list)
    permissions: PermissionSpec = Field(default_factory=PermissionSpec.default)
    context_cost: ContextCostSpec = Field(default_factory=ContextCostSpec)
    agent_card: AssetCardManifest = Field(default_factory=AssetCardManifest)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProfileManifest(ManifestModel):
    id: str
    target_host: str
    description: str | None = None
    includes: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class PackageManifest(ManifestModel):
    package: PackageInfo
    assets: list[AssetManifest] = Field(default_factory=list)
    profiles: list[ProfileManifest] = Field(default_factory=list)
