"""Tests for Phase 1 manifest validation behavior."""

from __future__ import annotations

from pathlib import Path

from aam.core.enums import (
    FilesystemPermission,
    LifecycleStatus,
    NetworkPermission,
    ShellPermission,
    TrustStatus,
    ValidationSeverity,
)
from aam.manifest.parser import parse_manifest
from aam.manifest.validator import validate_package
from aam.models.manifest import (
    AssetManifest,
    PackageInfo,
    PackageManifest,
    PermissionSpec,
    ProfileManifest,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _write_asset(package_root: Path, path: str, content: str = "asset\n") -> None:
    asset_path = package_root / path
    asset_path.parent.mkdir(parents=True, exist_ok=True)
    asset_path.write_text(content, encoding="utf-8")


def _package(
    *,
    assets: list[AssetManifest],
    profiles: list[ProfileManifest] | None = None,
) -> PackageManifest:
    return PackageManifest(
        package=PackageInfo(id="local.assets", name="Local Assets", version="0.1.0"),
        assets=assets,
        profiles=profiles or [],
    )


def _issue_codes(report_severity: ValidationSeverity, report) -> list[str]:
    return [
        issue.code
        for issue in report.issues
        if issue.severity is report_severity
    ]


def test_validator_reports_missing_asset_file(tmp_path: Path) -> None:
    manifest = _package(
        assets=[AssetManifest(id="missing", type="prompt", path="prompts/missing.md")]
    )

    report = validate_package(tmp_path, manifest)

    assert report.ok is False
    assert _issue_codes(ValidationSeverity.ERROR, report) == ["ASSET_PATH_MISSING"]
    assert report.issues[0].asset_id == "missing"
    assert report.issues[0].path == "assets[0].path"


def test_validator_reports_duplicate_asset_ids(tmp_path: Path) -> None:
    _write_asset(tmp_path, "prompts/one.md")
    _write_asset(tmp_path, "prompts/two.md")
    manifest = _package(
        assets=[
            AssetManifest(id="duplicate", type="prompt", path="prompts/one.md"),
            AssetManifest(id="duplicate", type="instruction", path="prompts/two.md"),
        ]
    )

    report = validate_package(tmp_path, manifest)

    assert report.ok is False
    assert _issue_codes(ValidationSeverity.ERROR, report) == ["DUPLICATE_ASSET_ID"]
    assert report.issues[0].asset_id == "duplicate"


def test_validator_reports_duplicate_profile_ids(tmp_path: Path) -> None:
    _write_asset(tmp_path, "agents/reviewer.md")
    manifest = _package(
        assets=[AssetManifest(id="reviewer", type="agent", path="agents/reviewer.md")],
        profiles=[
            ProfileManifest(id="review", target_host="codex"),
            ProfileManifest(id="review", target_host="claude_code"),
        ],
    )

    report = validate_package(tmp_path, manifest)

    assert report.ok is False
    assert _issue_codes(ValidationSeverity.ERROR, report) == ["DUPLICATE_PROFILE_ID"]
    assert report.issues[0].profile_id == "review"


def test_validator_reports_broken_depends_on_reference(tmp_path: Path) -> None:
    _write_asset(tmp_path, "agents/reviewer.md")
    manifest = _package(
        assets=[
            AssetManifest(
                id="reviewer",
                type="agent",
                path="agents/reviewer.md",
                depends_on=["asset:missing"],
            )
        ]
    )

    report = validate_package(tmp_path, manifest)

    assert report.ok is False
    assert _issue_codes(ValidationSeverity.ERROR, report) == [
        "BROKEN_DEPENDS_ON_REFERENCE"
    ]
    assert report.issues[0].asset_id == "reviewer"
    assert report.issues[0].path == "assets[0].depends_on[0]"


def test_validator_reports_broken_profile_include_reference(tmp_path: Path) -> None:
    _write_asset(tmp_path, "agents/reviewer.md")
    manifest = _package(
        assets=[AssetManifest(id="reviewer", type="agent", path="agents/reviewer.md")],
        profiles=[
            ProfileManifest(
                id="review",
                target_host="codex",
                includes=["asset:missing"],
            )
        ],
    )

    report = validate_package(tmp_path, manifest)

    assert report.ok is False
    assert _issue_codes(ValidationSeverity.ERROR, report) == [
        "BROKEN_PROFILE_INCLUDE_REFERENCE"
    ]
    assert report.issues[0].profile_id == "review"
    assert report.issues[0].path == "profiles[0].includes[0]"


def test_validator_reports_dependency_cycle(tmp_path: Path) -> None:
    _write_asset(tmp_path, "agents/a.md")
    _write_asset(tmp_path, "agents/b.md")
    _write_asset(tmp_path, "agents/c.md")
    manifest = _package(
        assets=[
            AssetManifest(id="a", type="agent", path="agents/a.md", depends_on=["b"]),
            AssetManifest(id="b", type="agent", path="agents/b.md", depends_on=["c"]),
            AssetManifest(id="c", type="agent", path="agents/c.md", depends_on=["a"]),
        ]
    )

    report = validate_package(tmp_path, manifest)

    assert report.ok is False
    assert _issue_codes(ValidationSeverity.ERROR, report) == ["DEPENDENCY_CYCLE"]
    assert "asset:a -> asset:b -> asset:c -> asset:a" in report.issues[0].message


def test_validator_reports_asset_path_escaping_package_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    manifest = _package(
        assets=[AssetManifest(id="escape", type="prompt", path="../outside.md")]
    )

    report = validate_package(tmp_path, manifest)

    assert report.ok is False
    assert _issue_codes(ValidationSeverity.ERROR, report) == [
        "ASSET_PATH_OUTSIDE_PACKAGE"
    ]
    assert report.issues[0].asset_id == "escape"


def test_validator_reports_expected_issues_from_fixture() -> None:
    package_root = FIXTURES / "validator_problem_package"
    manifest = parse_manifest(package_root)

    report = validate_package(package_root, manifest)

    assert report.ok is False
    assert _issue_codes(ValidationSeverity.ERROR, report) == [
        "ASSET_PATH_MISSING",
        "BROKEN_PROFILE_INCLUDE_REFERENCE",
        "DEPENDENCY_CYCLE",
    ]
    assert _issue_codes(ValidationSeverity.WARNING, report) == ["ASSET_BLOCKED"]


def test_validator_warns_for_risky_asset_states_and_broad_permissions(
    tmp_path: Path,
) -> None:
    _write_asset(tmp_path, "agents/blocked.md")
    _write_asset(tmp_path, "agents/unreviewed.md")
    _write_asset(tmp_path, "agents/archived.md")
    _write_asset(tmp_path, "agents/broad.md")
    manifest = _package(
        assets=[
            AssetManifest(
                id="blocked",
                type="agent",
                path="agents/blocked.md",
                trust_status=TrustStatus.BLOCKED,
            ),
            AssetManifest(
                id="unreviewed",
                type="agent",
                path="agents/unreviewed.md",
                trust_status=TrustStatus.UNREVIEWED,
            ),
            AssetManifest(
                id="archived",
                type="agent",
                path="agents/archived.md",
                lifecycle_status=LifecycleStatus.ARCHIVED,
            ),
            AssetManifest(
                id="broad",
                type="agent",
                path="agents/broad.md",
                permissions=PermissionSpec(
                    filesystem=FilesystemPermission.BROAD,
                    network=NetworkPermission.BROAD,
                    shell=ShellPermission.BROAD,
                ),
            ),
        ]
    )

    report = validate_package(tmp_path, manifest)

    assert report.ok is True
    assert _issue_codes(ValidationSeverity.WARNING, report) == [
        "ASSET_BLOCKED",
        "ASSET_UNREVIEWED",
        "ASSET_UNREVIEWED",
        "ASSET_ARCHIVED",
        "ASSET_UNREVIEWED",
        "BROAD_FILESYSTEM_PERMISSION",
        "BROAD_NETWORK_PERMISSION",
        "BROAD_SHELL_PERMISSION",
    ]
