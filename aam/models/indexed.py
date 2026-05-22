"""Indexed registry models for Phase 1."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from aam.core.enums import AssetType, AssetVisibility, LifecycleStatus, TrustStatus
from aam.models.asset_card import AssetCardProjection
from aam.models.graph import GraphProjection
from aam.models.manifest import ContextCostSpec, PermissionSpec, SourceProvenance
from aam.models.validation import ValidationReport


class IndexedModel(BaseModel):
    """Base model for indexed registry projections."""

    model_config = ConfigDict(extra="forbid")


class IndexedPackage(IndexedModel):
    id: str
    name: str
    version: str
    indexed_at: datetime
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    source: SourceProvenance


class IndexedAsset(IndexedModel):
    package_id: str
    package_version: str
    id: str
    qualified_id: str
    indexed_at: datetime
    type: AssetType
    path: str
    absolute_path: str
    visibility: AssetVisibility
    lifecycle_status: LifecycleStatus
    trust_status: TrustStatus
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    resolved_dependencies: list[str] = Field(default_factory=list)
    target_hosts: list[str] = Field(default_factory=list)
    permissions: PermissionSpec
    context_cost: ContextCostSpec
    content_hash: str
    source: SourceProvenance
    asset_card: AssetCardProjection


class IndexedProfile(IndexedModel):
    package_id: str
    package_version: str
    id: str
    qualified_id: str
    indexed_at: datetime
    target_host: str
    description: str | None = None
    includes: list[str] = Field(default_factory=list)
    resolved_includes: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class InMemoryRegistry(IndexedModel):
    packages: dict[str, IndexedPackage] = Field(default_factory=dict)
    assets: dict[str, IndexedAsset] = Field(default_factory=dict)
    profiles: dict[str, IndexedProfile] = Field(default_factory=dict)
    asset_cards: dict[str, AssetCardProjection] = Field(default_factory=dict)
    dependencies: dict[str, list[str]] = Field(default_factory=dict)
    reverse_dependencies: dict[str, list[str]] = Field(default_factory=dict)
    graph: GraphProjection = Field(default_factory=GraphProjection)
    validation_report: ValidationReport
