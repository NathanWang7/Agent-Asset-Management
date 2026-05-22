"""Tests for Phase 1 graph JSON projection."""

from __future__ import annotations

from pathlib import Path

from aam.graph.projection import build_graph_projection
from aam.registry.builder import build_registry

FIXTURES = Path(__file__).parent / "fixtures"


def _graph():
    registry = build_registry(FIXTURES / "valid_basic_package")
    return build_graph_projection(registry)


def test_graph_projection_is_json_ready_and_deterministic() -> None:
    first = _graph().model_dump(mode="json")
    second = _graph().model_dump(mode="json")

    assert first == second
    assert set(first) == {"nodes", "edges"}
    assert isinstance(first["nodes"], list)
    assert isinstance(first["edges"], list)


def test_graph_projection_contains_required_node_types() -> None:
    graph = _graph()

    node_types = {node.type.value for node in graph.nodes}

    assert {
        "package",
        "asset",
        "profile",
        "tag",
        "target_host",
        "source",
        "trust_status",
        "lifecycle_status",
    }.issubset(node_types)


def test_graph_projection_contains_required_edge_types() -> None:
    graph = _graph()

    edge_types = {edge.type.value for edge in graph.edges}

    assert {
        "package_contains_asset",
        "package_contains_profile",
        "profile_includes_asset",
        "asset_depends_on_asset",
        "asset_has_tag",
        "profile_has_tag",
        "asset_targets_host",
        "asset_imported_from_source",
        "asset_has_trust_status",
        "asset_has_lifecycle_status",
    }.issubset(edge_types)


def test_graph_projection_uses_deterministic_node_and_edge_ids() -> None:
    graph = _graph()
    node_ids = [node.id for node in graph.nodes]
    edge_ids = [edge.id for edge in graph.edges]

    assert node_ids == sorted(node_ids)
    assert edge_ids == sorted(edge_ids)
    assert "package:personal-agent-assets" in node_ids
    assert "asset:personal-agent-assets:code-reviewer@0.1.0" in node_ids
    assert "profile:personal-agent-assets:coding-review@0.1.0" in node_ids
    assert (
        "asset_depends_on_asset:"
        "asset:personal-agent-assets:code-reviewer@0.1.0->"
        "asset:personal-agent-assets:coding-style-guide@0.1.0"
    ) in edge_ids


def test_registry_builder_attaches_graph_projection() -> None:
    registry = build_registry(FIXTURES / "valid_basic_package")

    assert registry.graph == build_graph_projection(registry)
