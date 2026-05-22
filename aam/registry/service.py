"""Query service for Phase 1 in-memory registries."""

from __future__ import annotations

from pathlib import Path

from aam.models.asset_card import AssetCardProjection
from aam.models.indexed import (
    IndexedAsset,
    IndexedPackage,
    IndexedProfile,
    InMemoryRegistry,
)
from aam.registry.builder import build_registry
from aam.registry.query import AssetFilters


class RegistryLookupError(LookupError):
    """Raised when a registry object cannot be found."""


class RegistryService:
    """Stable query boundary over an in-memory registry."""

    def __init__(self, registry: InMemoryRegistry) -> None:
        self._registry = registry

    @classmethod
    def from_package_root(cls, package_root: str | Path) -> RegistryService:
        return cls(build_registry(package_root))

    def list_packages(self) -> list[IndexedPackage]:
        return list(self._registry.packages.values())

    def get_package(self, package_id: str) -> IndexedPackage:
        try:
            return self._registry.packages[package_id]
        except KeyError as exc:
            raise RegistryLookupError(f"Package not found: {package_id}") from exc

    def list_assets(self, filters: AssetFilters | None = None) -> list[IndexedAsset]:
        assets = list(self._registry.assets.values())
        if filters is None:
            return assets
        return [asset for asset in assets if _asset_matches_filters(asset, filters)]

    def get_asset(self, asset_id: str) -> IndexedAsset:
        qualified_id = self._resolve_asset_id(asset_id)
        return self._registry.assets[qualified_id]

    def list_profiles(self) -> list[IndexedProfile]:
        return list(self._registry.profiles.values())

    def get_profile(self, profile_id: str) -> IndexedProfile:
        qualified_id = self._resolve_profile_id(profile_id)
        return self._registry.profiles[qualified_id]

    def get_asset_card(self, asset_id: str) -> AssetCardProjection:
        asset = self.get_asset(asset_id)
        return self._registry.asset_cards[asset.qualified_id]

    def get_dependencies(self, asset_id: str) -> list[IndexedAsset]:
        asset = self.get_asset(asset_id)
        return [
            self._registry.assets[dependency_id]
            for dependency_id in self._registry.dependencies[asset.qualified_id]
        ]

    def get_reverse_dependencies(self, asset_id: str) -> list[IndexedAsset]:
        asset = self.get_asset(asset_id)
        return [
            self._registry.assets[dependent_id]
            for dependent_id in self._registry.reverse_dependencies[asset.qualified_id]
        ]

    def _resolve_asset_id(self, asset_id: str) -> str:
        if asset_id in self._registry.assets:
            return asset_id
        matches = [
            qualified_id
            for qualified_id, asset in self._registry.assets.items()
            if asset.id == asset_id
        ]
        if len(matches) == 1:
            return matches[0]
        raise RegistryLookupError(f"Asset not found: {asset_id}")

    def _resolve_profile_id(self, profile_id: str) -> str:
        if profile_id in self._registry.profiles:
            return profile_id
        matches = [
            qualified_id
            for qualified_id, profile in self._registry.profiles.items()
            if profile.id == profile_id
        ]
        if len(matches) == 1:
            return matches[0]
        raise RegistryLookupError(f"Profile not found: {profile_id}")


def _asset_matches_filters(asset: IndexedAsset, filters: AssetFilters) -> bool:
    if filters.type is not None and asset.type is not filters.type:
        return False
    if filters.tag is not None and filters.tag not in asset.tags:
        return False
    if (
        filters.trust_status is not None
        and asset.trust_status is not filters.trust_status
    ):
        return False
    if (
        filters.lifecycle_status is not None
        and asset.lifecycle_status is not filters.lifecycle_status
    ):
        return False
    if (
        filters.target_host is not None
        and filters.target_host not in asset.target_hosts
    ):
        return False
    return True
