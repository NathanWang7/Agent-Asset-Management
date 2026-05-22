"""Package validation for Phase 1 manifests."""

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
from aam.manifest.resolver import ReferenceResolver
from aam.models.manifest import AssetManifest, PackageManifest
from aam.models.validation import ValidationIssue, ValidationReport


def validate_package(
    package_root: str | Path,
    manifest: PackageManifest,
) -> ValidationReport:
    """Validate a typed package manifest against its package root."""
    root = Path(package_root)
    issues: list[ValidationIssue] = []
    resolver = ReferenceResolver(manifest)

    _validate_unique_asset_ids(manifest, issues)
    _validate_unique_profile_ids(manifest, issues)
    _validate_asset_paths(root, manifest, issues)
    dependency_edges = _validate_depends_on_references(manifest, resolver, issues)
    _validate_profile_include_references(manifest, resolver, issues)
    _validate_dependency_cycles(dependency_edges, manifest, issues)
    _validate_asset_warnings(manifest, issues)

    return ValidationReport(
        package_id=manifest.package.id,
        ok=not any(issue.severity is ValidationSeverity.ERROR for issue in issues),
        issues=issues,
    )


def _validate_unique_asset_ids(
    manifest: PackageManifest,
    issues: list[ValidationIssue],
) -> None:
    seen: set[str] = set()
    reported: set[str] = set()
    for index, asset in enumerate(manifest.assets):
        if asset.id in seen and asset.id not in reported:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="DUPLICATE_ASSET_ID",
                    message=f"Duplicate asset id: {asset.id}",
                    path=f"assets[{index}].id",
                    asset_id=asset.id,
                )
            )
            reported.add(asset.id)
        seen.add(asset.id)


def _validate_unique_profile_ids(
    manifest: PackageManifest,
    issues: list[ValidationIssue],
) -> None:
    seen: set[str] = set()
    reported: set[str] = set()
    for index, profile in enumerate(manifest.profiles):
        if profile.id in seen and profile.id not in reported:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="DUPLICATE_PROFILE_ID",
                    message=f"Duplicate profile id: {profile.id}",
                    path=f"profiles[{index}].id",
                    profile_id=profile.id,
                )
            )
            reported.add(profile.id)
        seen.add(profile.id)


def _validate_asset_paths(
    package_root: Path,
    manifest: PackageManifest,
    issues: list[ValidationIssue],
) -> None:
    resolved_root = package_root.resolve()
    for index, asset in enumerate(manifest.assets):
        if Path(asset.path).is_absolute():
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="ASSET_PATH_ABSOLUTE",
                    message=(
                        "Asset path must be relative to the package root: "
                        f"{asset.path}"
                    ),
                    path=f"assets[{index}].path",
                    asset_id=asset.id,
                )
            )
            continue

        resolved_path = _resolve_asset_path(resolved_root, asset.path)
        if not _is_within_package_root(resolved_root, resolved_path):
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="ASSET_PATH_OUTSIDE_PACKAGE",
                    message=(
                        f"Asset path points outside the package root: {asset.path}"
                    ),
                    path=f"assets[{index}].path",
                    asset_id=asset.id,
                )
            )
            continue

        if not resolved_path.is_file():
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="ASSET_PATH_MISSING",
                    message=f"Asset path does not exist: {asset.path}",
                    path=f"assets[{index}].path",
                    asset_id=asset.id,
                )
            )


def _validate_asset_warnings(
    manifest: PackageManifest,
    issues: list[ValidationIssue],
) -> None:
    for index, asset in enumerate(manifest.assets):
        if asset.trust_status is TrustStatus.BLOCKED:
            _append_asset_warning(
                issues,
                code="ASSET_BLOCKED",
                message=(
                    "Blocked asset will not be usable in future "
                    "assembly/materialization."
                ),
                path=f"assets[{index}].trust_status",
                asset=asset,
            )
        if asset.trust_status is TrustStatus.UNREVIEWED:
            _append_asset_warning(
                issues,
                code="ASSET_UNREVIEWED",
                message=(
                    "Unreviewed asset requires explicit warning in future "
                    "assembly/materialization."
                ),
                path=f"assets[{index}].trust_status",
                asset=asset,
            )
        if asset.lifecycle_status is LifecycleStatus.ARCHIVED:
            _append_asset_warning(
                issues,
                code="ASSET_ARCHIVED",
                message=(
                    "Archived asset should not participate in new plans by default."
                ),
                path=f"assets[{index}].lifecycle_status",
                asset=asset,
            )
        if asset.permissions.filesystem is FilesystemPermission.BROAD:
            _append_asset_warning(
                issues,
                code="BROAD_FILESYSTEM_PERMISSION",
                message="Asset declares broad filesystem permission.",
                path=f"assets[{index}].permissions.filesystem",
                asset=asset,
            )
        if asset.permissions.network is NetworkPermission.BROAD:
            _append_asset_warning(
                issues,
                code="BROAD_NETWORK_PERMISSION",
                message="Asset declares broad network permission.",
                path=f"assets[{index}].permissions.network",
                asset=asset,
            )
        if asset.permissions.shell is ShellPermission.BROAD:
            _append_asset_warning(
                issues,
                code="BROAD_SHELL_PERMISSION",
                message="Asset declares broad shell permission.",
                path=f"assets[{index}].permissions.shell",
                asset=asset,
            )


def _append_asset_warning(
    issues: list[ValidationIssue],
    *,
    code: str,
    message: str,
    path: str,
    asset: AssetManifest,
) -> None:
    issues.append(
        ValidationIssue(
            severity=ValidationSeverity.WARNING,
            code=code,
            message=message,
            path=path,
            asset_id=asset.id,
        )
    )


def _validate_depends_on_references(
    manifest: PackageManifest,
    resolver: ReferenceResolver,
    issues: list[ValidationIssue],
) -> dict[str, list[str]]:
    dependency_edges: dict[str, list[str]] = {asset.id: [] for asset in manifest.assets}
    for asset_index, asset in enumerate(manifest.assets):
        for reference_index, reference in enumerate(asset.depends_on):
            resolution = resolver.resolve_asset_reference(reference)
            if resolution.ok and resolution.asset_id is not None:
                dependency_edges.setdefault(asset.id, []).append(resolution.asset_id)
                continue

            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code=_dependency_reference_issue_code(resolution.issue_code),
                    message=resolution.message
                    or f"Unable to resolve dependency reference: {reference}",
                    path=f"assets[{asset_index}].depends_on[{reference_index}]",
                    asset_id=asset.id,
                )
            )
    return dependency_edges


def _validate_profile_include_references(
    manifest: PackageManifest,
    resolver: ReferenceResolver,
    issues: list[ValidationIssue],
) -> None:
    for profile_index, profile in enumerate(manifest.profiles):
        for reference_index, reference in enumerate(profile.includes):
            resolution = resolver.resolve_asset_reference(reference)
            if resolution.ok:
                continue

            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code=_profile_reference_issue_code(resolution.issue_code),
                    message=resolution.message
                    or f"Unable to resolve profile include reference: {reference}",
                    path=f"profiles[{profile_index}].includes[{reference_index}]",
                    profile_id=profile.id,
                )
            )


def _validate_dependency_cycles(
    dependency_edges: dict[str, list[str]],
    manifest: PackageManifest,
    issues: list[ValidationIssue],
) -> None:
    state: dict[str, str] = {}
    stack: list[str] = []

    def visit(asset_id: str) -> list[str] | None:
        if state.get(asset_id) == "visiting":
            return stack[stack.index(asset_id) :] + [asset_id]
        if state.get(asset_id) == "visited":
            return None

        state[asset_id] = "visiting"
        stack.append(asset_id)
        for dependency_id in dependency_edges.get(asset_id, []):
            cycle = visit(dependency_id)
            if cycle is not None:
                return cycle
        stack.pop()
        state[asset_id] = "visited"
        return None

    for asset in manifest.assets:
        cycle = visit(asset.id)
        if cycle is None:
            continue

        formatted_cycle = " -> ".join(f"asset:{asset_id}" for asset_id in cycle)
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="DEPENDENCY_CYCLE",
                message=f"Dependency cycle detected: {formatted_cycle}",
                asset_id=cycle[0],
            )
        )
        return


def _resolve_asset_path(package_root: Path, asset_path: str) -> Path:
    path = Path(asset_path)
    if path.is_absolute():
        return path.resolve()
    return (package_root / path).resolve()


def _is_within_package_root(package_root: Path, asset_path: Path) -> bool:
    try:
        asset_path.relative_to(package_root)
    except ValueError:
        return False
    return True


def _dependency_reference_issue_code(issue_code: str | None) -> str:
    if issue_code == "UNSUPPORTED_CROSS_PACKAGE_REFERENCE":
        return "UNSUPPORTED_DEPENDS_ON_REFERENCE"
    return "BROKEN_DEPENDS_ON_REFERENCE"


def _profile_reference_issue_code(issue_code: str | None) -> str:
    if issue_code == "UNSUPPORTED_CROSS_PACKAGE_REFERENCE":
        return "UNSUPPORTED_PROFILE_INCLUDE_REFERENCE"
    return "BROKEN_PROFILE_INCLUDE_REFERENCE"
