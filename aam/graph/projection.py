"""Lightweight deterministic graph projection for Phase 1 registries."""

from __future__ import annotations

import hashlib

from aam.core.enums import GraphEdgeType, GraphNodeType
from aam.models.graph import GraphEdge, GraphNode, GraphProjection
from aam.models.indexed import IndexedAsset, IndexedProfile, InMemoryRegistry
from aam.models.manifest import SourceProvenance


def build_graph_projection(registry: InMemoryRegistry) -> GraphProjection:
    """Build deterministic graph JSON projection from registry metadata."""
    nodes: dict[str, GraphNode] = {}
    edges: dict[str, GraphEdge] = {}

    for package in registry.packages.values():
        package_node_id = f"package:{package.id}"
        _add_node(
            nodes,
            GraphNode(
                id=package_node_id,
                type=GraphNodeType.PACKAGE,
                label=package.name,
                metadata={"version": package.version},
            ),
        )
        _add_source_node(nodes, package.source)

    for asset in registry.assets.values():
        _project_asset(nodes, edges, asset)

    for profile in registry.profiles.values():
        _project_profile(nodes, edges, profile)

    return GraphProjection(
        nodes=[nodes[node_id] for node_id in sorted(nodes)],
        edges=[edges[edge_id] for edge_id in sorted(edges)],
    )


def _project_asset(
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
    asset: IndexedAsset,
) -> None:
    package_node_id = f"package:{asset.package_id}"
    asset_node_id = _asset_node_id(asset.qualified_id)
    source_node_id = _source_node_id(asset.source)
    trust_node_id = f"trust_status:{asset.trust_status.value}"
    lifecycle_node_id = f"lifecycle_status:{asset.lifecycle_status.value}"

    _add_node(
        nodes,
        GraphNode(
            id=asset_node_id,
            type=GraphNodeType.ASSET,
            label=asset.id,
            metadata={"asset_type": asset.type.value},
        ),
    )
    _add_node(
        nodes,
        GraphNode(
            id=trust_node_id,
            type=GraphNodeType.TRUST_STATUS,
            label=asset.trust_status.value,
        ),
    )
    _add_node(
        nodes,
        GraphNode(
            id=lifecycle_node_id,
            type=GraphNodeType.LIFECYCLE_STATUS,
            label=asset.lifecycle_status.value,
        ),
    )
    _add_source_node(nodes, asset.source)

    _add_edge(
        edges,
        GraphEdgeType.PACKAGE_CONTAINS_ASSET,
        package_node_id,
        asset_node_id,
    )
    _add_edge(
        edges,
        GraphEdgeType.ASSET_IMPORTED_FROM_SOURCE,
        asset_node_id,
        source_node_id,
    )
    _add_edge(
        edges,
        GraphEdgeType.ASSET_HAS_TRUST_STATUS,
        asset_node_id,
        trust_node_id,
    )
    _add_edge(
        edges,
        GraphEdgeType.ASSET_HAS_LIFECYCLE_STATUS,
        asset_node_id,
        lifecycle_node_id,
    )

    for dependency_id in asset.resolved_dependencies:
        _add_edge(
            edges,
            GraphEdgeType.ASSET_DEPENDS_ON_ASSET,
            asset_node_id,
            _asset_node_id(dependency_id),
        )

    for tag in asset.tags:
        tag_node_id = f"tag:{tag}"
        _add_node(
            nodes,
            GraphNode(id=tag_node_id, type=GraphNodeType.TAG, label=tag),
        )
        _add_edge(edges, GraphEdgeType.ASSET_HAS_TAG, asset_node_id, tag_node_id)

    for target_host in asset.target_hosts:
        target_node_id = f"target_host:{target_host}"
        _add_node(
            nodes,
            GraphNode(
                id=target_node_id,
                type=GraphNodeType.TARGET_HOST,
                label=target_host,
            ),
        )
        _add_edge(
            edges,
            GraphEdgeType.ASSET_TARGETS_HOST,
            asset_node_id,
            target_node_id,
        )


def _project_profile(
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
    profile: IndexedProfile,
) -> None:
    package_node_id = f"package:{profile.package_id}"
    profile_node_id = f"profile:{profile.qualified_id}"
    _add_node(
        nodes,
        GraphNode(
            id=profile_node_id,
            type=GraphNodeType.PROFILE,
            label=profile.id,
            metadata={"target_host": profile.target_host},
        ),
    )
    _add_edge(
        edges,
        GraphEdgeType.PACKAGE_CONTAINS_PROFILE,
        package_node_id,
        profile_node_id,
    )

    for included_asset_id in profile.resolved_includes:
        _add_edge(
            edges,
            GraphEdgeType.PROFILE_INCLUDES_ASSET,
            profile_node_id,
            _asset_node_id(included_asset_id),
        )

    for tag in profile.tags:
        tag_node_id = f"tag:{tag}"
        _add_node(
            nodes,
            GraphNode(id=tag_node_id, type=GraphNodeType.TAG, label=tag),
        )
        _add_edge(edges, GraphEdgeType.PROFILE_HAS_TAG, profile_node_id, tag_node_id)


def _add_source_node(
    nodes: dict[str, GraphNode],
    source: SourceProvenance,
) -> None:
    node_id = _source_node_id(source)
    _add_node(
        nodes,
        GraphNode(
            id=node_id,
            type=GraphNodeType.SOURCE,
            label=source.kind.value,
            metadata={
                "original_location": source.original_location,
                "resolved_ref": source.resolved_ref,
            },
        ),
    )


def _source_node_id(source: SourceProvenance) -> str:
    identity = source.resolved_ref or source.original_location or source.kind.value
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
    return f"source:{source.kind.value}:{digest}"


def _asset_node_id(qualified_id: str) -> str:
    return f"asset:{qualified_id}"


def _add_node(nodes: dict[str, GraphNode], node: GraphNode) -> None:
    nodes[node.id] = node


def _add_edge(
    edges: dict[str, GraphEdge],
    edge_type: GraphEdgeType,
    source: str,
    target: str,
) -> None:
    edge_id = f"{edge_type.value}:{source}->{target}"
    edges[edge_id] = GraphEdge(
        id=edge_id,
        type=edge_type,
        source=source,
        target=target,
    )
