"""Graph projection models for Phase 1."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from aam.core.enums import GraphEdgeType, GraphNodeType


class GraphModel(BaseModel):
    """Base model for graph projection objects."""

    model_config = ConfigDict(extra="forbid")


class GraphNode(GraphModel):
    id: str
    type: GraphNodeType
    label: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(GraphModel):
    id: str
    type: GraphEdgeType
    source: str
    target: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphProjection(GraphModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
