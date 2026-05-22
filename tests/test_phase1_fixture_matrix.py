"""Tests protecting the required Phase 1 fixture matrix."""

from __future__ import annotations

from pathlib import Path

import pytest

from aam.core.enums import ValidationSeverity
from aam.manifest.parser import parse_manifest
from aam.manifest.validator import validate_package

FIXTURES = Path(__file__).parent / "fixtures"

REQUIRED_PHASE_1_FIXTURES = {
    "valid_basic_package": {"errors": set(), "warnings": {"ASSET_UNREVIEWED"}},
    "invalid_missing_file": {"errors": {"ASSET_PATH_MISSING"}, "warnings": set()},
    "invalid_broken_dependency": {
        "errors": {"BROKEN_DEPENDS_ON_REFERENCE"},
        "warnings": set(),
    },
    "invalid_broken_profile_include": {
        "errors": {"BROKEN_PROFILE_INCLUDE_REFERENCE"},
        "warnings": set(),
    },
    "invalid_cycle": {"errors": {"DEPENDENCY_CYCLE"}, "warnings": set()},
    "valid_unreviewed_import_like_package": {
        "errors": set(),
        "warnings": {"ASSET_UNREVIEWED"},
    },
    "valid_blocked_asset_package": {
        "errors": set(),
        "warnings": {"ASSET_BLOCKED"},
    },
    "invalid_path_escape": {
        "errors": {"ASSET_PATH_OUTSIDE_PACKAGE"},
        "warnings": set(),
    },
}


@pytest.mark.parametrize("fixture_name", REQUIRED_PHASE_1_FIXTURES)
def test_required_phase_1_fixture_directory_exists(fixture_name: str) -> None:
    assert (FIXTURES / fixture_name).is_dir()


@pytest.mark.parametrize(
    ("fixture_name", "expected"),
    REQUIRED_PHASE_1_FIXTURES.items(),
)
def test_required_phase_1_fixture_represents_expected_scenario(
    fixture_name: str,
    expected: dict[str, set[str]],
) -> None:
    package_root = FIXTURES / fixture_name
    manifest = parse_manifest(package_root)

    report = validate_package(package_root, manifest)

    error_codes = {
        issue.code
        for issue in report.issues
        if issue.severity is ValidationSeverity.ERROR
    }
    warning_codes = {
        issue.code
        for issue in report.issues
        if issue.severity is ValidationSeverity.WARNING
    }
    assert error_codes == expected["errors"]
    assert warning_codes == expected["warnings"]
