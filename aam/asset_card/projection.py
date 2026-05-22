"""Deterministic Asset Card projection builder."""

from __future__ import annotations

from aam.manifest.resolver import ReferenceResolver
from aam.models.asset_card import AssetCardProjection
from aam.models.manifest import AssetManifest, PackageManifest


def build_asset_card_projection(
    *,
    manifest: PackageManifest,
    asset: AssetManifest,
    content_hash: str,
) -> AssetCardProjection:
    """Build an Asset Card projection from manifest metadata."""
    return AssetCardProjection(
        id=asset.id,
        package_id=manifest.package.id,
        version=manifest.package.version,
        type=asset.type,
        title=asset.agent_card.title or asset.id,
        summary=asset.agent_card.summary or asset.description,
        intended_use=list(asset.agent_card.intended_use),
        input_context=dict(asset.agent_card.input_context),
        output_capabilities=list(asset.agent_card.output_capabilities),
        tags=list(asset.tags),
        target_hosts=list(asset.target_hosts),
        dependencies=_resolve_dependencies(manifest, asset),
        trust_status=asset.trust_status,
        lifecycle_status=asset.lifecycle_status,
        visibility=asset.visibility,
        permissions=asset.permissions,
        risk_level=asset.agent_card.risk_level,
        estimated_context_cost=asset.context_cost.estimated_tokens,
        content_hash=content_hash,
        source=manifest.package.source,
    )


def _resolve_dependencies(manifest: PackageManifest, asset: AssetManifest) -> list[str]:
    resolver = ReferenceResolver(manifest)
    dependencies: list[str] = []
    for reference in asset.depends_on:
        resolution = resolver.resolve_asset_reference(reference)
        if not resolution.ok or resolution.canonical is None:
            raise ValueError(f"Unable to resolve dependency reference: {reference}")
        dependencies.append(resolution.canonical)
    return dependencies
