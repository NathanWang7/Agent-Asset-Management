"""Core enum definitions for Agent Asset Management."""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """String enum base for stable manifest values."""


class AssetType(StrEnum):
    PROMPT = "prompt"
    AGENT = "agent"
    SKILL = "skill"
    TOOL = "tool"
    MCP_SERVER = "mcp_server"
    WORKFLOW = "workflow"
    INSTRUCTION = "instruction"
    KNOWLEDGE = "knowledge"
    EVAL_CASE = "eval_case"
    TEMPLATE = "template"
    SCHEMA = "schema"
    HOST_INSTRUCTION_PACK = "host_instruction_pack"
    OTHER = "other"


class AssetVisibility(StrEnum):
    INTERNAL = "internal"
    EXPORTED = "exported"
    SHARED = "shared"


class LifecycleStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class TrustStatus(StrEnum):
    TRUSTED = "trusted"
    UNREVIEWED = "unreviewed"
    SANDBOX_ONLY = "sandbox_only"
    BLOCKED = "blocked"
    NEEDS_MANUAL_REVIEW = "needs_manual_review"


class FilesystemPermission(StrEnum):
    NONE = "none"
    READ = "read"
    WRITE = "write"
    BROAD = "broad"


class NetworkPermission(StrEnum):
    NONE = "none"
    READ = "read"
    BROAD = "broad"


class ShellPermission(StrEnum):
    NONE = "none"
    LIMITED = "limited"
    BROAD = "broad"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class SourceKind(StrEnum):
    MANUAL_CREATED = "manual_created"
    LOCAL_DIRECTORY = "local_directory"
    GITHUB_REPOSITORY = "github_repository"
    UNKNOWN = "unknown"


class GraphNodeType(StrEnum):
    PACKAGE = "package"
    ASSET = "asset"
    PROFILE = "profile"
    TAG = "tag"
    TARGET_HOST = "target_host"
    SOURCE = "source"
    TRUST_STATUS = "trust_status"
    LIFECYCLE_STATUS = "lifecycle_status"


class GraphEdgeType(StrEnum):
    PACKAGE_CONTAINS_ASSET = "package_contains_asset"
    PACKAGE_CONTAINS_PROFILE = "package_contains_profile"
    PROFILE_INCLUDES_ASSET = "profile_includes_asset"
    ASSET_DEPENDS_ON_ASSET = "asset_depends_on_asset"
    ASSET_HAS_TAG = "asset_has_tag"
    PROFILE_HAS_TAG = "profile_has_tag"
    ASSET_TARGETS_HOST = "asset_targets_host"
    ASSET_IMPORTED_FROM_SOURCE = "asset_imported_from_source"
    ASSET_HAS_TRUST_STATUS = "asset_has_trust_status"
    ASSET_HAS_LIFECYCLE_STATUS = "asset_has_lifecycle_status"


class ValidationSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
