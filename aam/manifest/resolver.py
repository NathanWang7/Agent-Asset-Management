"""Reference resolution for Phase 1 package manifests."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from aam.models.manifest import PackageManifest


class AssetReferenceResolution(BaseModel):
    """Result of resolving a manifest asset reference."""

    model_config = ConfigDict(extra="forbid")

    reference: str
    ok: bool
    is_local: bool
    is_supported: bool
    asset_id: str | None = None
    package_id: str | None = None
    version: str | None = None
    canonical: str | None = None
    issue_code: str | None = None
    message: str | None = None


class ReferenceResolver:
    """Resolve asset references against one package manifest."""

    def __init__(self, manifest: PackageManifest) -> None:
        self._manifest = manifest
        self._asset_ids = {asset.id for asset in manifest.assets}

    def resolve_asset_reference(self, reference: str) -> AssetReferenceResolution:
        """Resolve a Phase 1 asset reference."""
        if reference.startswith("asset:"):
            return self._resolve_explicit_asset_reference(reference)
        return self._resolve_local_asset_reference(
            reference=reference,
            asset_id=reference,
        )

    def _resolve_explicit_asset_reference(
        self,
        reference: str,
    ) -> AssetReferenceResolution:
        body = reference.removeprefix("asset:")
        if "/" in body:
            package_id, asset_with_version = body.split("/", 1)
            asset_id, version = _split_version(asset_with_version)
            return AssetReferenceResolution(
                reference=reference,
                ok=False,
                is_local=False,
                is_supported=False,
                package_id=package_id or None,
                asset_id=asset_id or None,
                version=version,
                issue_code="UNSUPPORTED_CROSS_PACKAGE_REFERENCE",
                message=(
                    "Cross-package asset references are reserved for a future phase."
                ),
            )

        return self._resolve_local_asset_reference(reference=reference, asset_id=body)

    def _resolve_local_asset_reference(
        self,
        *,
        reference: str,
        asset_id: str,
    ) -> AssetReferenceResolution:
        if asset_id in self._asset_ids:
            return AssetReferenceResolution(
                reference=reference,
                ok=True,
                is_local=True,
                is_supported=True,
                package_id=self._manifest.package.id,
                asset_id=asset_id,
                version=self._manifest.package.version,
                canonical=(
                    f"{self._manifest.package.id}:"
                    f"{asset_id}@{self._manifest.package.version}"
                ),
            )

        return AssetReferenceResolution(
            reference=reference,
            ok=False,
            is_local=True,
            is_supported=True,
            package_id=self._manifest.package.id,
            asset_id=asset_id or None,
            version=self._manifest.package.version,
            issue_code="UNKNOWN_ASSET_REFERENCE",
            message=f"Unknown asset reference: {reference}",
        )


def _split_version(value: str) -> tuple[str, str | None]:
    if "@" not in value:
        return value, None
    asset_id, version = value.rsplit("@", 1)
    return asset_id, version or None
