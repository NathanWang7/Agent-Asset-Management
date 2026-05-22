"""Build Phase 1 in-memory registries from package manifests."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from aam.asset_card.projection import build_asset_card_projection
from aam.hash.content_hash import compute_content_hash
from aam.manifest.parser import parse_manifest
from aam.manifest.resolver import ReferenceResolver
from aam.manifest.validator import validate_package
from aam.models.indexed import (
    IndexedAsset,
    IndexedPackage,
    IndexedProfile,
    InMemoryRegistry,
)
from aam.models.manifest import AssetManifest, PackageManifest, ProfileManifest
from aam.models.validation import ValidationReport


class RegistryBuildError(ValueError):
    """Raised when validation errors prevent registry construction."""

    def __init__(self, validation_report: ValidationReport) -> None:
        super().__init__("Package validation failed; registry was not built.")
        self.validation_report = validation_report


def build_registry(package_root: str | Path) -> InMemoryRegistry:
    """Parse, validate, and index a package into an in-memory registry."""
    root = Path(package_root)
    manifest = parse_manifest(root)
    validation_report = validate_package(root, manifest)
    if not validation_report.ok:
        raise RegistryBuildError(validation_report)

    package = _build_indexed_package(manifest)
    assets = _build_indexed_assets(root, manifest)
    profiles = _build_indexed_profiles(manifest)
    dependencies = {
        qualified_id: list(asset.resolved_dependencies)
        for qualified_id, asset in assets.items()
    }
    reverse_dependencies = _build_reverse_dependencies(
        assets.keys(),
        dependencies,
    )

    return InMemoryRegistry(
        packages={package.id: package},
        assets=assets,
        profiles=profiles,
        asset_cards={
            qualified_id: asset.asset_card for qualified_id, asset in assets.items()
        },
        dependencies=dependencies,
        reverse_dependencies=reverse_dependencies,
        validation_report=validation_report,
    )


def _build_indexed_package(manifest: PackageManifest) -> IndexedPackage:
    package = manifest.package
    return IndexedPackage(
        id=package.id,
        name=package.name,
        version=package.version,
        description=package.description,
        tags=list(package.tags),
        source=package.source,
    )


def _build_indexed_assets(
    package_root: Path,
    manifest: PackageManifest,
) -> dict[str, IndexedAsset]:
    return {
        _asset_qualified_id(manifest, asset): _build_indexed_asset(
            package_root,
            manifest,
            asset,
        )
        for asset in manifest.assets
    }


def _build_indexed_asset(
    package_root: Path,
    manifest: PackageManifest,
    asset: AssetManifest,
) -> IndexedAsset:
    absolute_path = (package_root / asset.path).resolve()
    content_hash = compute_content_hash(absolute_path)
    asset_card = build_asset_card_projection(
        manifest=manifest,
        asset=asset,
        content_hash=content_hash,
    )
    qualified_id = _asset_qualified_id(manifest, asset)
    return IndexedAsset(
        package_id=manifest.package.id,
        package_version=manifest.package.version,
        id=asset.id,
        qualified_id=qualified_id,
        type=asset.type,
        path=asset.path,
        absolute_path=str(absolute_path),
        visibility=asset.visibility,
        lifecycle_status=asset.lifecycle_status,
        trust_status=asset.trust_status,
        description=asset.description,
        tags=list(asset.tags),
        depends_on=list(asset.depends_on),
        resolved_dependencies=list(asset_card.dependencies),
        target_hosts=list(asset.target_hosts),
        permissions=asset.permissions,
        context_cost=asset.context_cost,
        content_hash=content_hash,
        source=manifest.package.source,
        asset_card=asset_card,
    )


def _build_indexed_profiles(
    manifest: PackageManifest,
) -> dict[str, IndexedProfile]:
    resolver = ReferenceResolver(manifest)
    return {
        _profile_qualified_id(manifest, profile): _build_indexed_profile(
            manifest,
            profile,
            resolver,
        )
        for profile in manifest.profiles
    }


def _build_indexed_profile(
    manifest: PackageManifest,
    profile: ProfileManifest,
    resolver: ReferenceResolver,
) -> IndexedProfile:
    resolved_includes: list[str] = []
    for reference in profile.includes:
        resolution = resolver.resolve_asset_reference(reference)
        if not resolution.ok or resolution.canonical is None:
            # Validation and resolver output should make this unreachable.
            raise ValueError(
                f"Unable to resolve profile include reference: {reference}"
            )
        resolved_includes.append(resolution.canonical)

    return IndexedProfile(
        package_id=manifest.package.id,
        package_version=manifest.package.version,
        id=profile.id,
        qualified_id=_profile_qualified_id(manifest, profile),
        target_host=profile.target_host,
        description=profile.description,
        includes=list(profile.includes),
        resolved_includes=resolved_includes,
        tags=list(profile.tags),
    )


def _build_reverse_dependencies(
    asset_ids: Iterable[str],
    dependencies: dict[str, list[str]],
) -> dict[str, list[str]]:
    reverse_dependencies = {asset_id: [] for asset_id in asset_ids}
    for asset_id, dependency_ids in dependencies.items():
        for dependency_id in dependency_ids:
            if dependency_id not in reverse_dependencies:
                # Validation and resolver output should make this unreachable.
                raise ValueError(
                    f"Resolved dependency is not indexed: {dependency_id}"
                )
            reverse_dependencies[dependency_id].append(asset_id)
    return reverse_dependencies


def _asset_qualified_id(manifest: PackageManifest, asset: AssetManifest) -> str:
    return f"{manifest.package.id}:{asset.id}@{manifest.package.version}"


def _profile_qualified_id(manifest: PackageManifest, profile: ProfileManifest) -> str:
    return f"{manifest.package.id}:{profile.id}@{manifest.package.version}"
