"""Tests for Phase 1 manifest reference resolution."""

from __future__ import annotations

from aam.manifest.resolver import ReferenceResolver
from aam.models.manifest import AssetManifest, PackageInfo, PackageManifest


def _manifest() -> PackageManifest:
    return PackageManifest(
        package=PackageInfo(id="local.assets", name="Local Assets", version="0.1.0"),
        assets=[
            AssetManifest(id="reviewer", type="agent", path="agents/reviewer.md"),
            AssetManifest(id="style-guide", type="instruction", path="docs/style.md"),
        ],
    )


def test_resolves_shorthand_asset_reference() -> None:
    resolution = ReferenceResolver(_manifest()).resolve_asset_reference("reviewer")

    assert resolution.ok is True
    assert resolution.is_local is True
    assert resolution.is_supported is True
    assert resolution.asset_id == "reviewer"
    assert resolution.canonical == "local.assets:reviewer@0.1.0"


def test_resolves_explicit_asset_reference() -> None:
    resolution = ReferenceResolver(_manifest()).resolve_asset_reference(
        "asset:style-guide"
    )

    assert resolution.ok is True
    assert resolution.is_local is True
    assert resolution.is_supported is True
    assert resolution.asset_id == "style-guide"
    assert resolution.canonical == "local.assets:style-guide@0.1.0"


def test_identifies_future_cross_package_reference_without_accepting_it() -> None:
    resolution = ReferenceResolver(_manifest()).resolve_asset_reference(
        "asset:shared.pkg/common-reviewer@2.0.0"
    )

    assert resolution.ok is False
    assert resolution.is_local is False
    assert resolution.is_supported is False
    assert resolution.package_id == "shared.pkg"
    assert resolution.asset_id == "common-reviewer"
    assert resolution.version == "2.0.0"
    assert resolution.canonical is None
    assert resolution.issue_code == "UNSUPPORTED_CROSS_PACKAGE_REFERENCE"


def test_rejects_unknown_local_asset_reference() -> None:
    resolution = ReferenceResolver(_manifest()).resolve_asset_reference("asset:missing")

    assert resolution.ok is False
    assert resolution.is_local is True
    assert resolution.is_supported is True
    assert resolution.asset_id == "missing"
    assert resolution.canonical is None
    assert resolution.issue_code == "UNKNOWN_ASSET_REFERENCE"
