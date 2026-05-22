"""Tests for Phase 1 registry query service."""

from __future__ import annotations

from pathlib import Path

import pytest

from aam.registry.builder import build_registry
from aam.registry.service import AssetFilters, RegistryLookupError, RegistryService

FIXTURES = Path(__file__).parent / "fixtures"


def _service() -> RegistryService:
    return RegistryService(build_registry(FIXTURES / "valid_basic_package"))


def test_service_builds_from_package_root() -> None:
    service = RegistryService.from_package_root(FIXTURES / "valid_basic_package")

    assert service.get_package("personal-agent-assets").id == "personal-agent-assets"


def test_service_lists_and_gets_registry_objects() -> None:
    service = _service()

    assert [package.id for package in service.list_packages()] == [
        "personal-agent-assets"
    ]
    assert service.get_package("personal-agent-assets").version == "0.1.0"
    assert [asset.id for asset in service.list_assets()] == [
        "code-reviewer",
        "coding-style-guide",
    ]
    assert service.get_asset("code-reviewer").qualified_id == (
        "personal-agent-assets:code-reviewer@0.1.0"
    )
    assert [profile.id for profile in service.list_profiles()] == ["coding-review"]
    assert service.get_profile("coding-review").target_host == "codex"
    assert service.get_asset_card("code-reviewer").title == "Code Reviewer"


def test_service_returns_dependencies_and_reverse_dependencies() -> None:
    service = _service()

    assert [asset.id for asset in service.get_dependencies("code-reviewer")] == [
        "coding-style-guide"
    ]
    assert service.get_dependencies("coding-style-guide") == []
    assert [
        asset.id for asset in service.get_reverse_dependencies("coding-style-guide")
    ] == ["code-reviewer"]


def test_service_filters_assets() -> None:
    service = _service()

    assert [asset.id for asset in service.list_assets(AssetFilters(type="agent"))] == [
        "code-reviewer"
    ]
    assert [asset.id for asset in service.list_assets(AssetFilters(tag="review"))] == [
        "code-reviewer"
    ]
    assert [
        asset.id for asset in service.list_assets(AssetFilters(trust_status="trusted"))
    ] == ["code-reviewer"]
    assert [
        asset.id
        for asset in service.list_assets(AssetFilters(lifecycle_status="draft"))
    ] == ["coding-style-guide"]
    assert [
        asset.id for asset in service.list_assets(AssetFilters(target_host="codex"))
    ] == ["code-reviewer"]


def test_service_reports_missing_assets_clearly() -> None:
    service = _service()

    with pytest.raises(RegistryLookupError, match="Asset not found: missing"):
        service.get_asset("missing")
