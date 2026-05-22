"""Tests for Phase 1 in-memory registry construction."""

from __future__ import annotations

from pathlib import Path

import pytest

from aam.registry.builder import (
    RegistryBuildError,
    _build_reverse_dependencies,
    build_registry,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_build_registry_from_valid_package() -> None:
    registry = build_registry(FIXTURES / "valid_basic_package")

    assert registry.validation_report.ok is True
    assert list(registry.packages) == ["personal-agent-assets"]
    assert list(registry.assets) == [
        "personal-agent-assets:code-reviewer@0.1.0",
        "personal-agent-assets:coding-style-guide@0.1.0",
    ]
    assert list(registry.profiles) == [
        "personal-agent-assets:coding-review@0.1.0"
    ]

    package = registry.packages["personal-agent-assets"]
    assert package.id == "personal-agent-assets"
    assert package.version == "0.1.0"
    assert package.tags == ["personal", "coding"]

    asset = registry.assets["personal-agent-assets:code-reviewer@0.1.0"]
    assert asset.id == "code-reviewer"
    assert asset.qualified_id == "personal-agent-assets:code-reviewer@0.1.0"
    assert asset.absolute_path.endswith("agents/code_reviewer.md")
    assert asset.content_hash.startswith("sha256:")
    assert asset.asset_card.content_hash == asset.content_hash
    assert asset.asset_card.title == "Code Reviewer"


def test_registry_dependencies_and_reverse_dependencies_are_canonical() -> None:
    registry = build_registry(FIXTURES / "valid_basic_package")

    reviewer_id = "personal-agent-assets:code-reviewer@0.1.0"
    style_id = "personal-agent-assets:coding-style-guide@0.1.0"

    assert registry.dependencies == {
        reviewer_id: [style_id],
        style_id: [],
    }
    assert registry.reverse_dependencies == {
        reviewer_id: [],
        style_id: [reviewer_id],
    }
    assert registry.assets[reviewer_id].resolved_dependencies == [style_id]


def test_registry_profiles_resolve_includes() -> None:
    registry = build_registry(FIXTURES / "valid_basic_package")

    profile = registry.profiles["personal-agent-assets:coding-review@0.1.0"]

    assert profile.id == "coding-review"
    assert profile.resolved_includes == [
        "personal-agent-assets:code-reviewer@0.1.0",
        "personal-agent-assets:coding-style-guide@0.1.0",
    ]


def test_build_registry_raises_on_validation_errors() -> None:
    with pytest.raises(RegistryBuildError) as error:
        build_registry(FIXTURES / "validator_problem_package")

    report = error.value.validation_report
    assert report.ok is False
    error_codes = [
        issue.code for issue in report.issues if issue.severity.value == "error"
    ]
    assert error_codes == [
        "ASSET_PATH_MISSING",
        "BROKEN_PROFILE_INCLUDE_REFERENCE",
        "DEPENDENCY_CYCLE",
    ]


def test_reverse_dependency_guard_reports_unindexed_dependency() -> None:
    dependencies = {
        "package:asset-a@0.1.0": ["package:missing@0.1.0"],
    }

    with pytest.raises(ValueError, match="Resolved dependency is not indexed"):
        _build_reverse_dependencies(["package:asset-a@0.1.0"], dependencies)
