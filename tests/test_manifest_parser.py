"""Tests for Phase 1 manifest parser behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

from aam.core.enums import AssetType, AssetVisibility, SourceKind, TrustStatus
from aam.manifest.parser import ManifestParseError, parse_manifest

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_manifest_reads_valid_basic_fixture() -> None:
    manifest = parse_manifest(FIXTURES / "valid_basic_package")

    assert manifest.package.id == "personal-agent-assets"
    assert manifest.package.version == "0.1.0"
    assert manifest.package.source.kind is SourceKind.MANUAL_CREATED
    assert [asset.id for asset in manifest.assets] == [
        "code-reviewer",
        "coding-style-guide",
    ]
    assert manifest.assets[0].type is AssetType.AGENT
    assert manifest.assets[0].visibility is AssetVisibility.EXPORTED
    assert manifest.assets[0].trust_status is TrustStatus.TRUSTED
    assert manifest.assets[0].depends_on == ["asset:coding-style-guide"]
    assert manifest.assets[1].type is AssetType.INSTRUCTION
    assert manifest.assets[1].visibility is AssetVisibility.INTERNAL
    assert manifest.assets[1].trust_status is TrustStatus.UNREVIEWED
    assert [profile.id for profile in manifest.profiles] == ["coding-review"]
    assert manifest.profiles[0].includes == [
        "asset:code-reviewer",
        "asset:coding-style-guide",
    ]


def test_parse_manifest_reports_invalid_yaml() -> None:
    with pytest.raises(ManifestParseError) as error:
        parse_manifest(FIXTURES / "invalid_yaml")

    message = str(error.value)
    assert "Invalid YAML" in message
    assert "package.yaml" in message
    assert error.value.path == FIXTURES / "invalid_yaml" / "package.yaml"


def test_parse_manifest_reports_missing_required_model_field() -> None:
    with pytest.raises(ManifestParseError) as error:
        parse_manifest(FIXTURES / "invalid_missing_required_field")

    message = str(error.value)
    assert "Invalid manifest schema" in message
    assert "package.id" in message
    assert error.value.path == (
        FIXTURES / "invalid_missing_required_field" / "package.yaml"
    )


def test_parse_manifest_reports_missing_package_yaml() -> None:
    with pytest.raises(ManifestParseError) as error:
        parse_manifest(FIXTURES)

    assert "package.yaml not found" in str(error.value)
    assert error.value.path == FIXTURES / "package.yaml"
