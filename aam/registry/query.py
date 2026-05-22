"""Query filter models for registry assets."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from aam.core.enums import AssetType, LifecycleStatus, TrustStatus


class AssetFilters(BaseModel):
    """Optional filters for asset listing."""

    model_config = ConfigDict(extra="forbid")

    type: AssetType | None = None
    tag: str | None = None
    trust_status: TrustStatus | None = None
    lifecycle_status: LifecycleStatus | None = None
    target_host: str | None = None
