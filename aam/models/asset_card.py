"""Typed Asset Card projection model for Phase 1."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from aam.core.enums import (
    AssetType,
    AssetVisibility,
    LifecycleStatus,
    RiskLevel,
    TrustStatus,
)
from aam.models.manifest import PermissionSpec, SourceProvenance


class AssetCardProjection(BaseModel):
    """Deterministic projection of manifest metadata for an asset."""

    model_config = ConfigDict(extra="forbid")

    id: str
    package_id: str
    version: str
    type: AssetType
    title: str
    summary: str | None = None
    intended_use: list[str] = Field(default_factory=list)
    input_context: dict[str, Any] = Field(default_factory=dict)
    output_capabilities: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    target_hosts: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    trust_status: TrustStatus
    lifecycle_status: LifecycleStatus
    visibility: AssetVisibility
    permissions: PermissionSpec
    risk_level: RiskLevel
    estimated_context_cost: int | None = None
    content_hash: str
    source: SourceProvenance
