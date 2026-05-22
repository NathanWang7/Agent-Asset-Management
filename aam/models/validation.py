"""Typed validation result models for Phase 1 package validation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from aam.core.enums import ValidationSeverity


class ValidationModel(BaseModel):
    """Base model for validation result objects."""

    model_config = ConfigDict(extra="forbid")


class ValidationIssue(ValidationModel):
    severity: ValidationSeverity
    code: str
    message: str
    path: str | None = None
    asset_id: str | None = None
    profile_id: str | None = None


class ValidationReport(ValidationModel):
    package_id: str | None = None
    ok: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
