# Phase 2 Persistent Registry, Import Service & CLI Usability Implementation Spec

## 1. 状态

Draft v0.1

本文档是 Agent Asset Management 项目的 **Phase 2 实施规格文档**。

本文档不是产品简报，也不是长期路线图，而是 Phase 1.5 Technical Spike Checkpoint 完成后，用于指导 Codex / Claude Code / 其他 AI coding agent 执行 Phase 2 的阶段级工程文档。

Phase 2 的主题是：

> Persistent Registry, Import Service & CLI Usability

Phase 2 的核心目标是把 Phase 1 的 in-memory package / registry 能力升级为 workspace-scoped、SQLite-backed、可重建、可查询、可审计的本地 registry，并实现本地目录与 GitHub public source 的正式导入入口。

Phase 2 结束后，系统仍不需要具备 HTTP API、MCP Server、Web UI、Profile Assembly、Package Lock 或 materialization 能力；但必须提供后续 Phase 3-7 可以稳定复用的 registry store、query service、import service、event placeholder 和 CLI 工作流。

---

## 2. 权威输入文档

Phase 2 implementation 必须直接消费 Phase 0 / Phase 1 / Phase 1.5 的既有决策，不应重新定义项目方向、核心概念或技术栈。

### 2.1 Overall 文档

```text
dev_docs/overall/agent_asset_management_foundation_spec_v0.4.1.md
dev_docs/overall/agent_asset_management_product_brief_v0.3.2.md
```

### 2.2 Phase 1 文档

```text
dev_docs/phase1/phase_1_core_package_system_mvp_implementation_spec.md
docs/phase1_quickstart.md
```

### 2.3 Phase 1.5 文档

```text
dev_docs/phase1.5/phase_1_5_technical_spike_checkpoint_implementation_spec.md
dev_docs/phase1.5/phase_1_handoff_review.md
dev_docs/phase1.5/adr_0001_registry_storage.md
dev_docs/phase1.5/registry_schema_draft.md
dev_docs/phase1.5/adr_0002_usage_audit_rejection_events.md
dev_docs/phase1.5/adr_0003_api_and_mcp_framework.md
dev_docs/phase1.5/adr_0004_composition_assembly_lock_boundary.md
dev_docs/phase1.5/profile_assembly_lock_complexity_note.md
dev_docs/phase1.5/adr_0006_ci_and_release_convention.md
dev_docs/phase1.5/phase_1_5_technical_spike_note.md
dev_docs/phase1.5/phase_1_5_closeout_checklist.md
```

如果某些 Phase 1.5 产物在实际仓库中尚未存在，Phase 2 开始前应先补齐或在 Phase 2 PR 中明确列为 blocker。Phase 2 不应在缺失基础决策的情况下重新做 spike。

### 2.4 Phase 2 文档

Phase 2 新增开发文档应放在：

```text
dev_docs/phase2/
```

本 spec 的目标路径为：

```text
dev_docs/phase2/phase_2_persistent_registry_import_service_cli_usability_implementation_spec.md
```

Phase 2 的 review prompt 应放在：

```text
dev_docs/review/phase_2_claude_pr_review_prompt.md
```

用户可见的使用文档可以放入：

```text
docs/
```

Phase 2 的 ADR、内部设计说明、closeout checklist、review report 默认不放入 `docs/`。

---

## 3. 阶段定位

Phase 2 是从“一个 package 的临时 in-memory 查询闭环”走向“workspace 级本地资产库”的阶段。

Phase 1 已经建立：

```text
package.yaml
  -> typed models
  -> parser
  -> validator
  -> content hash
  -> Asset Card projection
  -> in-memory registry
  -> graph projection
  -> CLI query/demo
```

Phase 2 应建立：

```text
workspace root
  -> .aam/registry.sqlite3
  -> registry rebuild
  -> persistent RegistryStore
  -> stable query services
  -> import service
  -> ImportRun report
  -> Usage/Audit/Rejection event placeholders
  -> enhanced CLI
```

Phase 2 的工程重点不是“写一个数据库缓存”，而是建立后续所有能力复用的本地 registry core：

```text
Manifest + Asset files + Source provenance + ImportRun
  -> Parser / Validator / Index Builder
  -> SQLite RegistryStore
  -> RegistryService / AssetQueryService / GraphQueryService / StatsService
  -> CLI now
  -> API / MCP / Web UI later
```

Phase 2 结束时，CLI、未来 API、未来 MCP Server 和未来 Web UI 都应能复用同一组 service boundary，而不是各自扫描文件或各自访问内部表。

---

## 4. 目标

Phase 2 的目标是完成本地 persistent registry、正式 import workflow 和增强 CLI 的最小闭环。

更具体地说，Phase 2 应让用户能够：

1. 初始化一个 AAM workspace。
2. 在 workspace 下生成 `.aam/registry.sqlite3`。
3. 将一个或多个 Phase 1 package index 到 SQLite registry。
4. 删除 registry 后可以 deterministic rebuild。
5. 通过 query service 查询 package、asset、profile、Asset Card、dependencies、reverse dependencies 和 graph projection。
6. 查看 asset / package / profile 的基本统计。
7. 查看 orphan assets、broken references、validation issues 等基础诊断信息。
8. 从本地目录 adopt import 资产。
9. 从本地目录 copy/snapshot import 资产。
10. 从 GitHub public repo/path/ref import 资产。
11. GitHub 导入时将 branch / tag / ref 解析到 concrete commit SHA。
12. 导入过程生成 ImportRun report。
13. imported assets 默认进入 `unreviewed` 或 `needs_manual_review`，不能默认 trusted。
14. 在 registry 中预留 UsageEvent / AuditLog / RejectionEvent 的 append-only placeholder。
15. 通过 CLI 执行 workspace init、registry rebuild、import、stats、list、show、graph export 等流程。
16. 通过 `--json` 获得 deterministic machine-readable output。

Phase 2 的工程目标是让 registry 变成后续阶段的稳定基础设施，而不是做完整产品体验。

---

## 5. 核心设计原则

### 5.1 Manifest as Source of Truth

`package.yaml`、asset files、source provenance 和 import run records 是事实来源。

SQLite registry 是 workspace-local query projection，可以删除并从事实来源重建。任何 Phase 2 实现都不得把 SQLite registry 变成唯一不可重建的事实源。

### 5.2 Registry as Query Projection

RegistryStore 是查询投影层，服务 CLI、未来 API、未来 MCP 和未来 UI。

Phase 2 不应让 CLI、import service、stats service 或 graph query 各自重新扫描文件。扫描、解析、校验、hash、projection 应由既有 parser / validator / registry builder / rebuild pipeline 统一处理。

### 5.3 One Workspace, One Registry DB

Phase 2 采用 workspace-scoped SQLite registry：

```text
<workspace-root>/.aam/registry.sqlite3
```

Phase 2 不设计 multi-workspace shared DB，不设计 team registry，不设计 server-side registry。

### 5.4 Deterministic Rebuild

给定相同 manifest、asset files 和 source provenance，registry rebuild 的逻辑结果应保持确定性。

允许 `indexed_at`、`created_at`、`updated_at` 等明确 volatile 字段变化，但 deterministic JSON export / snapshot tests 应能归一化这些字段。

### 5.5 Source-aware Import

导入不是简单复制文件。Import workflow 必须记录：

- source kind；
- original location；
- resolved version anchor；
- imported timestamp；
- detected assets；
- generated wrapper manifest；
- warnings / errors；
- trust defaults；
- imported package identity。

GitHub import 必须 pin 到 resolved commit SHA。

### 5.6 Trust before Import Automation

外部导入资产默认不可信。

Phase 2 可以允许用户显式设置导入默认 trust policy，但默认策略应是：

```text
local adopted package with native manifest:
  preserve manifest trust status, but do not silently promote missing trust to trusted.

local copied/snapshot imported package:
  default imported/generated assets to unreviewed or needs_manual_review.

GitHub imported package:
  default imported/generated assets to unreviewed or needs_manual_review.
```

### 5.7 Service Boundary before API/MCP/UI

Phase 2 不做 production HTTP API、MCP Server 或 Web UI，但必须为它们准备稳定服务层。

未来 Phase 4A / 4B / 6 应使用 Phase 2 的 RegistryService / QueryService / ImportService，而不是重写 registry access。

### 5.8 Event Placeholder, not Governance Workflow

Phase 2 应创建 UsageEvent / AuditLog / RejectionEvent 的最小 append-only placeholder，但不做 recommendation learning、完整 governance workflow 或 Web UI rejection handling。

---

## 6. Scope

Phase 2 包含以下能力。

### 6.1 Workspace Layout

定义 workspace 最小目录：

```text
my-aam-workspace/
  .aam/
    registry.sqlite3
    imports/
      runs/
    packages/
      imported/
      snapshots/
```

说明：

- `.aam/registry.sqlite3` 是 SQLite registry store。
- `.aam/imports/runs/` 可保存 ImportRun report JSON。
- `.aam/packages/imported/` 可保存 generated wrapper manifest 和 imported package metadata。
- `.aam/packages/snapshots/` 可保存 copy/snapshot 模式复制进来的资产文件。
- Phase 2 可先采用简化 layout，但必须在代码和文档中明确 workspace boundary。

### 6.2 RegistryStore

实现 SQLite-backed `RegistryStore`。

RegistryStore 负责：

- 初始化 schema；
- 存储 indexed packages；
- 存储 indexed assets；
- 存储 indexed profiles；
- 存储 Asset Card projections；
- 存储 resolved dependencies；
- 存储 profile includes；
- 存储 graph nodes / edges；
- 存储 validation issues；
- 存储 minimal event placeholders；
- 提供 transactional rebuild write；
- 提供 read-only query primitives。

RegistryStore 不负责：

- 解析 manifest；
- 校验 package；
- 计算 content hash；
- 生成 Asset Card；
- 生成 graph projection；
- 实现 import detection；
- 选择 assembly assets；
- 生成 lockfile。

### 6.3 Registry Schema

Phase 2 最小表：

```text
registry_meta
registry_packages
registry_assets
registry_profiles
registry_asset_cards
registry_asset_dependencies
registry_profile_includes
registry_graph_nodes
registry_graph_edges
registry_validation_issues
registry_usage_events
registry_audit_log
registry_rejection_events
```

Phase 2 可以把复杂结构序列化为 deterministic JSON text。不要过早规范化所有字段。

### 6.4 Registry Rebuild

实现 registry rebuild pipeline：

```text
package roots / imported package roots
  -> parse manifests
  -> validate packages
  -> build in-memory indexed projections
  -> open SQLite transaction
  -> replace affected package projections
  -> write packages/assets/profiles/cards/dependencies/graph/issues
  -> commit
```

失败时必须 rollback，不允许写入半完成 registry projection。

### 6.5 Query Services

实现稳定查询服务：

```text
RegistryService
AssetQueryService
GraphQueryService
StatsService
```

服务层应面向未来 API / MCP / UI，而不是只服务 CLI human output。

### 6.6 Import Service

实现正式 import workflow。

最小支持：

```text
SourceAdapter interface
LocalDirectorySourceAdapter
GitHubSourceAdapter v0
ImportService
ImportRun report
```

导入模式：

```text
local adopt
local copy/snapshot
github public repo/path/ref
```

### 6.7 Event Placeholder Store

实现 append-only placeholder：

```text
UsageEvent
AuditLog
RejectionEvent
```

Phase 2 至少支持写入和查询最近事件，供未来 API/MCP/UI 使用。

### 6.8 CLI Usability

增强 CLI：

```bash
aam workspace init <workspace-dir>
aam registry rebuild <workspace-dir>
aam registry stats <workspace-dir> [--json]
aam registry graph export <workspace-dir> [--json]

aam import local <source-dir> --workspace <workspace-dir> --mode adopt
aam import local <source-dir> --workspace <workspace-dir> --mode copy
aam import github <repo-url> --ref <branch-or-tag-or-sha> --workspace <workspace-dir>

aam list assets --workspace <workspace-dir> [filters] [--json]
aam list profiles --workspace <workspace-dir> [filters] [--json]
aam show asset <asset-id> --workspace <workspace-dir> [--json]
aam show card <asset-id> --workspace <workspace-dir> [--json]
aam show dependencies <asset-id> --workspace <workspace-dir> [--json]
aam show reverse-dependencies <asset-id> --workspace <workspace-dir> [--json]
```

如果已有 Phase 1 CLI command shape 与上述不同，Phase 2 可以适度调整，但必须保持：

- human-readable output 可读；
- JSON output deterministic；
- CLI 调用 service boundary；
- CLI 不直接实现 registry business logic。

---

## 7. Non-goals

Phase 2 明确不做以下内容：

1. 不做 production HTTP API。
2. 不做 MCP Server。
3. 不做 Web UI。
4. 不做 graph visualization UI。
5. 不做 Dashboard。
6. 不做 Profile closure。
7. 不做 DiscoveryRequest / AssemblyPlan / PackageLock 的 production implementation。
8. 不做 materialization。
9. 不做 target-specific host adapter。
10. 不做 GitHub private repo auth。
11. 不做 GitHub branch 自动更新 tracking。
12. 不做 complex upstream merge / upgrade workflow。
13. 不做 semantic search。
14. 不做 embedding index。
15. 不做 duplicate detection 的智能算法。
16. 不做 asset editing。
17. 不做 manifest writer。
18. 不做 full governance workflow。
19. 不做 team workspace。
20. 不做 remote registry server。
21. 不做 public marketplace。
22. 不做 agent runtime。

Phase 2 可以为这些能力保留字段、表、接口和事件占位，但不得把完整实现塞入本阶段。

---

## 8. Proposed Package Layout

建议 Phase 2 在 Phase 1 package layout 基础上新增或扩展：

```text
aam/
  workspace/
    __init__.py
    layout.py
    service.py
    errors.py

  registry/
    __init__.py
    builder.py             # Phase 1 existing, reused
    service.py             # facade over store/query services
    query.py               # asset/package/profile/card queries
    graph_query.py
    stats.py
    store.py               # SQLite RegistryStore
    schema.py
    migrations.py
    rebuild.py
    json_codec.py

  importing/
    __init__.py
    models.py
    source_adapter.py
    service.py
    local_directory.py
    github.py
    manifest_writer.py     # generated wrapper manifest only, not general UI editing
    import_run.py

  events/
    __init__.py
    models.py
    store.py

  cli/
    __init__.py
    main.py
    commands.py
    formatters.py

tests/
  fixtures/
    phase2/
      workspace_basic/
      local_import_native_package/
      local_import_unstructured_assets/
      github_import_sample_repo/
      invalid_import_source/

  test_workspace_layout.py
  test_registry_store_schema.py
  test_registry_rebuild.py
  test_registry_query_service.py
  test_graph_query_service.py
  test_stats_service.py
  test_event_placeholder_store.py
  test_source_adapter_contract.py
  test_local_import.py
  test_github_import.py
  test_phase2_cli_smoke.py
```

说明：

- `workspace/` 只负责 workspace root、`.aam/` layout 和 workspace metadata。
- `registry/store.py` 只负责 SQLite persistence primitives。
- `registry/rebuild.py` 负责编排 Phase 1 parser / validator / builder 到 RegistryStore 的写入。
- `registry/query.py` 不应重新解析 manifest。
- `importing/` 负责 source inspection、wrapper manifest generation、ImportRun report。
- `events/` 只实现 placeholder，不承担 governance workflow。
- `cli/` 只调用 workspace / registry / importing / event services。

---

## 9. Workspace Contract

### 9.1 Workspace Layout

```text
<workspace-root>/
  .aam/
    workspace.json
    registry.sqlite3
    imports/
      runs/
    packages/
      imported/
      snapshots/
```

### 9.2 `workspace.json`

Phase 2 可选但推荐写入 workspace metadata：

```json
{
  "schema_version": "1",
  "workspace_id": "local-generated-id",
  "created_at": "2026-05-27T00:00:00Z",
  "updated_at": "2026-05-27T00:00:00Z"
}
```

规则：

- `workspace_id` 不是跨用户全局身份，只是本地诊断和 future migration 辅助字段。
- `workspace_id` 可以进入 event placeholder。
- Phase 2 不实现 remote workspace 或 team workspace。

### 9.3 WorkspaceService

建议接口：

```python
class WorkspaceService:
    @classmethod
    def init(cls, workspace_root: Path) -> WorkspaceInfo: ...

    @classmethod
    def open(cls, workspace_root: Path) -> WorkspaceContext: ...

    def registry_path(self) -> Path: ...
    def imports_dir(self) -> Path: ...
    def imported_packages_dir(self) -> Path: ...
    def snapshots_dir(self) -> Path: ...
```

验收要求：

- init 不应覆盖已有 workspace，除非显式 `--force`。
- open 不应自动创建缺失 workspace，除非 CLI command 明确是 init。
- workspace path 应 resolve 到真实路径，用于 event 和 registry metadata。

---

## 10. RegistryStore Contract

### 10.1 RegistryStore Responsibility

`RegistryStore` 是 SQLite persistence boundary。

建议接口：

```python
class RegistryStore:
    @classmethod
    def connect(cls, db_path: Path) -> RegistryStore: ...

    def initialize_schema(self) -> None: ...
    def get_schema_version(self) -> str: ...

    def rebuild_packages(self, projections: list[PackageRegistryProjection]) -> RebuildResult: ...

    def list_packages(self) -> list[IndexedPackage]: ...
    def get_package(self, package_id: str) -> IndexedPackage: ...

    def list_assets(self, filters: AssetQueryFilters | None = None) -> list[IndexedAsset]: ...
    def get_asset(self, asset_ref: str) -> IndexedAsset: ...
    def get_asset_card(self, asset_ref: str) -> AssetCardProjection: ...

    def list_profiles(self, filters: ProfileQueryFilters | None = None) -> list[IndexedProfile]: ...
    def get_profile(self, profile_ref: str) -> IndexedProfile: ...

    def get_dependencies(self, asset_ref: str) -> list[IndexedAsset]: ...
    def get_reverse_dependencies(self, asset_ref: str) -> list[IndexedAsset]: ...

    def export_graph(self) -> GraphProjection: ...
    def list_validation_issues(self, filters: ValidationIssueFilters | None = None) -> list[ValidationIssue]: ...
```

### 10.2 Store Rules

1. Enums are persisted as stable text values.
2. Structured fields use deterministic JSON text.
3. Writes occur inside explicit transactions.
4. Rebuild should replace all projections for affected packages atomically.
5. Read APIs should return typed domain models or typed DTOs, not raw SQLite rows.
6. Store should not call parser, validator, content hash, or graph projection directly.
7. Store should expose enough primitives for query services but not leak SQL into CLI.

### 10.3 Registry Meta

Minimum metadata keys:

```text
schema_version
workspace_root
created_at
updated_at
```

Optional metadata keys:

```text
last_rebuild_at
last_rebuild_package_count
last_rebuild_asset_count
last_rebuild_status
```

---

## 11. Deterministic JSON Contract

Phase 2 应统一 JSON serialization policy。

Rules:

1. Sort object keys.
2. Preserve list order from manifest or projection builders.
3. Use UTF-8.
4. Serialize enum values as strings.
5. Represent timestamps as UTC ISO-8601 strings.
6. Avoid volatile fields in snapshot outputs unless explicitly part of the projection.
7. Include schema/export version metadata in exported files.

Recommended helper:

```python
def dumps_deterministic(value: Any) -> str: ...
def loads_json(value: str) -> Any: ...
```

CLI `--json` output must use the same policy or a shared output formatter that preserves deterministic field order where practical.

---

## 12. Registry Rebuild Contract

### 12.1 Inputs

Registry rebuild can be invoked with:

```text
workspace root
package roots
imported package roots
rebuild options
```

Phase 2 can start with full workspace rebuild and defer package-level incremental rebuild.

### 12.2 Rebuild Workflow

```text
1. Resolve workspace context.
2. Discover registered package roots or use explicit package roots.
3. Parse package manifests with existing parser.
4. Validate packages with existing validator.
5. Build in-memory registry projection with existing builder.
6. Convert projection into store rows.
7. Open SQLite transaction.
8. Delete or replace rows for rebuilt packages.
9. Insert packages/assets/profiles/cards/dependencies/profile_includes/graph/issues.
10. Update registry_meta.
11. Commit.
12. Return RebuildResult.
```

### 12.3 Failure Rules

- YAML parse error: rebuild fails for that package and must not write partial package projection.
- Validation error: rebuild fails unless future option explicitly allows indexing invalid packages; Phase 2 default should fail closed.
- SQLite write error: transaction rollback.
- Missing asset file: validation error.
- Broken dependency: validation error.
- Unsupported cross-package reference: warning or error according to Phase 1 resolver behavior; Phase 2 must not silently accept.

### 12.4 RebuildResult

```python
class RebuildResult(BaseModel):
    workspace_root: Path
    registry_path: Path
    started_at: datetime
    completed_at: datetime | None
    ok: bool
    package_count: int
    asset_count: int
    profile_count: int
    issue_count: int
    errors: list[RegistryRebuildError]
    warnings: list[RegistryRebuildWarning]
```

---

## 13. Query Service Contract

### 13.1 RegistryService

`RegistryService` 是应用层 facade。

建议职责：

- open workspace；
- connect RegistryStore；
- expose query service instances；
- coordinate rebuild；
- provide stable boundary for CLI / future API / future MCP / future UI。

### 13.2 AssetQueryService

Capabilities:

```text
list_packages
get_package
list_assets
get_asset
get_asset_card
list_profiles
get_profile
get_dependencies
get_reverse_dependencies
filter assets by type / tag / trust / lifecycle / target_host / source_kind / package_id
```

Filters:

```python
class AssetQueryFilters(BaseModel):
    package_id: str | None = None
    type: str | None = None
    tags: list[str] = []
    trust_status: str | None = None
    lifecycle_status: str | None = None
    target_host: str | None = None
    source_kind: str | None = None
    visibility: str | None = None
```

Rules:

- Tag matching default: asset must contain all requested tags.
- Target host matching: asset target_hosts contains requested host.
- Empty filters list all assets.
- Missing asset should return typed not-found error.
- Query output should be deterministic by default, sorted by package_id / asset_id or qualified_id.

### 13.3 GraphQueryService

Capabilities:

```text
export full graph projection
get nodes by type
get edges by type
get asset ego relations
get profile includes graph slice
```

Phase 2 does not implement graph layout or visualization.

Minimum output:

```json
{
  "schema_version": "1",
  "nodes": [],
  "edges": []
}
```

### 13.4 StatsService

Minimum stats:

```text
package_count
asset_count
profile_count
asset_count_by_type
asset_count_by_trust_status
asset_count_by_lifecycle_status
asset_count_by_source_kind
asset_count_by_target_host
orphan_asset_count
broken_reference_count
validation_issue_count
```

Definitions:

- `orphan_asset`: asset not included by any profile and not depended on by any other asset.
- `broken_reference`: validation issue with broken dependency, broken profile include, missing file, or unsupported reference code.
- `top_reused_assets`: optional in Phase 2; can be deferred if query cost or semantics are unclear.

---

## 14. Event Placeholder Contract

Phase 2 should implement minimal append-only event placeholders.

### 14.1 Event Principles

1. Append-only by default.
2. No recommendation learning in Phase 2.
3. No full governance workflow in Phase 2.
4. Events support future Agent Gateway audit, rejection-to-governance, degraded-mode diagnostics and materialization policy logging.
5. Events should be cheap to write and easy to query by recent time.

### 14.2 Common Fields

```python
class EventActor(BaseModel):
    actor_type: Literal["human", "cli", "agent", "system", "unknown"]
    actor_id: str | None = None
    client_name: str | None = None
```

Common event fields:

```text
workspace_id
event_id / audit_id / rejection_id
occurred_at
actor_type
actor_id
client_name
metadata_json
```

### 14.3 UsageEvent

Purpose:

- Future asset usage tracking.
- Future agent recommendation acceptance diagnostics.
- Future materialization and gateway analytics.

Minimum shape:

```python
class UsageEvent(BaseModel):
    event_id: str
    workspace_id: str
    occurred_at: datetime
    actor: EventActor
    action: str
    target_type: str
    target_id: str | None
    result: Literal["success", "failure", "skipped", "unknown"]
    reason_code: str | None = None
    metadata: dict[str, Any] = {}
```

### 14.4 AuditLog

Purpose:

- Future policy decision audit.
- Future Agent Gateway audit.
- Future materialization decision records.

Minimum shape:

```python
class AuditLog(BaseModel):
    audit_id: str
    workspace_id: str
    occurred_at: datetime
    actor: EventActor
    operation: str
    target_type: str
    target_id: str | None
    decision: str | None
    result: Literal["allowed", "denied", "failed", "unknown"]
    policy_snapshot_ref: str | None = None
    metadata: dict[str, Any] = {}
```

### 14.5 RejectionEvent

Purpose:

- Future rejection-to-governance loop.
- Future repeated bad recommendation suppression.
- Future review workflow.

Minimum shape:

```python
class RejectionEvent(BaseModel):
    rejection_id: str
    workspace_id: str
    occurred_at: datetime
    actor: EventActor
    rejected_target_type: str
    rejected_target_id: str
    reason_code: str
    note: str | None = None
    follow_up_action: Literal["ignore_once", "review_now", "block_asset", "none", "unknown"]
    metadata: dict[str, Any] = {}
```

Phase 2 CLI can expose a minimal internal command or test-only service for appending events. It does not need a user-facing rejection UX.

---

## 15. Import Model

### 15.1 Import Concepts

```text
Source
SourceAdapter
ImportRequest
SourceInspection
DetectedAssetCandidate
GeneratedManifestPlan
ImportRun
ImportRunReport
ImportedPackage
```

### 15.2 ImportRequest

```python
class ImportRequest(BaseModel):
    workspace_root: Path
    source_kind: SourceKind
    source_location: str
    ref: str | None = None
    path: str | None = None
    mode: Literal["adopt", "copy", "snapshot"]
    package_id: str | None = None
    package_name: str | None = None
    trust_default: TrustStatus | None = None
    dry_run: bool = False
```

### 15.3 SourceInspection

```python
class SourceInspection(BaseModel):
    source_kind: SourceKind
    original_location: str
    resolved_ref: str | None
    detected_native_package: bool
    detected_package_root: Path | None
    candidate_assets: list[DetectedAssetCandidate]
    warnings: list[ImportWarning]
    errors: list[ImportError]
```

### 15.4 ImportRunReport

```python
class ImportRunReport(BaseModel):
    import_run_id: str
    workspace_id: str
    started_at: datetime
    completed_at: datetime | None
    ok: bool
    source_kind: SourceKind
    original_location: str
    requested_ref: str | None
    resolved_ref: str | None
    mode: str
    package_id: str | None
    package_root: Path | None
    generated_manifest_path: Path | None
    imported_asset_count: int
    warnings: list[ImportWarning]
    errors: list[ImportError]
    trust_default: TrustStatus
```

### 15.5 Import Rules

1. Import must not silently mark external assets trusted.
2. Import should generate a report even on failure where possible.
3. Import should not mutate source directory in adopt mode, except when user explicitly asks to create wrapper metadata in workspace.
4. Copy/snapshot mode should write to workspace-managed package area.
5. GitHub import must record resolved commit SHA.
6. Generated wrapper manifest must preserve source provenance.
7. Import should trigger or instruct registry rebuild after successful import.
8. Import dry-run should not write files or registry rows.

---

## 16. SourceAdapter Contracts

### 16.1 SourceAdapter Interface

```python
class SourceAdapter(Protocol):
    source_kind: SourceKind

    def inspect(self, request: ImportRequest) -> SourceInspection: ...

    def import_source(self, request: ImportRequest) -> ImportRunReport: ...
```

Adapters should not write registry rows directly. ImportService coordinates adapter output and registry rebuild.

### 16.2 LocalDirectorySourceAdapter

Supported modes:

```text
adopt
copy
snapshot
```

#### Adopt mode

Meaning:

- Existing directory remains in place.
- If it contains native `package.yaml`, import registers package root.
- If it does not contain native manifest, adapter may generate wrapper manifest under workspace imported package area that references or copies detected assets according to mode.

Rules:

- Do not copy source files.
- Do not rewrite source files.
- Preserve source original_location.
- Trust default should be conservative for generated assets.

#### Copy / Snapshot mode

Meaning:

- Copy selected source files into workspace-managed snapshot directory.
- Generate package manifest around copied files.
- Registry indexes managed copy.

Rules:

- Do not overwrite existing snapshot package unless explicit unique package_id or force behavior is defined.
- Preserve source original_location.
- Record snapshot timestamp.
- Generated assets default to `unreviewed` or `needs_manual_review`.

### 16.3 GitHubSourceAdapter v0

Supported inputs:

```text
repo URL
ref: branch | tag | commit SHA
optional path within repo
```

Required behavior:

1. Resolve requested ref to concrete commit SHA.
2. Download or checkout public repo/path content into workspace-managed import area.
3. Detect native package manifest if present.
4. Otherwise generate wrapper manifest.
5. Store source provenance:

```text
kind: github_repository or github_path
original_location: repo URL + optional path
resolved_ref: commit SHA
```

6. Default imported/generated assets to `unreviewed` or `needs_manual_review`.
7. Produce ImportRun report.

Non-goals:

- No private repo auth.
- No GitHub API rate-limit management beyond basic failure message.
- No branch tracking.
- No automatic upgrade.
- No merge with previous import.
- No dependency installation.

---

## 17. Generated Wrapper Manifest Policy

Phase 2 may generate wrapper manifests for imported sources that do not already conform to AAM native package structure.

### 17.1 Wrapper Manifest Responsibilities

Wrapper manifest should:

- declare package identity;
- declare source provenance;
- declare detected assets;
- assign conservative trust defaults;
- preserve paths relative to generated package root;
- use stable asset ids where possible;
- include import metadata in `metadata` fields where useful。

### 17.2 Asset Detection Heuristic v0

Phase 2 should keep detection simple.

Possible rules:

```text
*.md under prompts/        -> prompt
*.md under agents/         -> agent
*.md under skills/         -> skill
*.md named AGENTS.md       -> host_instruction_pack or instruction
*.md named CLAUDE.md       -> host_instruction_pack or instruction
*.json with mcp in name    -> mcp_server or tool candidate
*.yaml / *.yml config      -> tool / template / other candidate
```

Detection must produce candidates and warnings, not pretend to infer perfect semantics.

If asset type is uncertain, use `other` with warning.

### 17.3 Generated IDs

Generated package id:

```text
imported-<source-slug>-<short-hash>
```

Generated asset id:

```text
<type>.<file-stem-slug>
```

If collision occurs, append deterministic short hash.

### 17.4 Trust Defaults

Default for GitHub generated assets:

```text
trust_status: unreviewed
lifecycle_status: active
visibility: exported or internal depending on detection confidence
risk_level: unknown
```

Default for local generated assets:

```text
trust_status: unreviewed or needs_manual_review
```

Native package import should preserve manifest-provided trust status, but missing fields should use Phase 1 defaults rather than silent trusted.

---

## 18. CLI Contract

### 18.1 Workspace Commands

```bash
aam workspace init <workspace-dir>
aam workspace info <workspace-dir> [--json]
```

Expected behavior:

- `init` creates `.aam/` layout and initializes registry schema.
- `info` prints workspace root, registry path, schema version, package count if available.

### 18.2 Registry Commands

```bash
aam registry rebuild <workspace-dir> [--package-root <path>] [--json]
aam registry stats <workspace-dir> [--json]
aam registry graph export <workspace-dir> [--json]
aam registry issues <workspace-dir> [--json]
```

Expected behavior:

- `rebuild` populates SQLite registry.
- `stats` uses StatsService.
- `graph export` uses GraphQueryService.
- `issues` returns validation issues stored from last rebuild.

### 18.3 Import Commands

```bash
aam import local <source-dir> --workspace <workspace-dir> --mode adopt [--dry-run] [--json]
aam import local <source-dir> --workspace <workspace-dir> --mode copy [--dry-run] [--json]
aam import github <repo-url> --workspace <workspace-dir> --ref <ref> [--path <path>] [--dry-run] [--json]
```

Expected behavior:

- import creates ImportRun report.
- dry-run does not write files or registry rows.
- successful import should either trigger rebuild or print explicit next command; default recommended behavior is to rebuild imported package projection after import.

### 18.4 Query Commands

```bash
aam list assets --workspace <workspace-dir> [--type <type>] [--tag <tag>] [--trust <status>] [--target-host <host>] [--json]
aam list profiles --workspace <workspace-dir> [--target-host <host>] [--json]
aam show asset <asset-id> --workspace <workspace-dir> [--json]
aam show card <asset-id> --workspace <workspace-dir> [--json]
aam show dependencies <asset-id> --workspace <workspace-dir> [--json]
aam show reverse-dependencies <asset-id> --workspace <workspace-dir> [--json]
```

### 18.5 CLI Output Rules

Human-readable output:

- concise summary first;
- warnings clearly marked;
- no full asset content by default;
- show next suggested command after import/rebuild where useful。

JSON output:

- deterministic serialization;
- include schema version;
- no absolute path leakage unless command is local diagnostic and user requested full detail;
- tests should assert parseable JSON。

---

## 19. Work Orders

Phase 2 应拆成以下 10 个 Work Orders。每个 Work Order 应对应一个 GitHub issue、一个 branch 和一个 PR。

---

### WO1 — Phase 2 Spec and Review Prompt

目标：冻结 Phase 2 的工程边界和 AI PR review 标准。

交付物：

```text
dev_docs/phase2/phase_2_persistent_registry_import_service_cli_usability_implementation_spec.md
dev_docs/review/phase_2_claude_pr_review_prompt.md
```

任务：

1. 写入本 implementation spec。
2. 写 Phase 2 Claude PR review prompt。
3. 明确 authoritative docs。
4. 明确 Phase 2 scope / non-goals。
5. 明确 work order list。
6. 明确 review checklist。

验收标准：

- Spec 可以直接指导 WO2-WO10。
- Review prompt 明确禁止 API/MCP/UI/Assembly/Lockfile 越界。
- 文档路径遵守 `dev_docs/phase2/` 和 `dev_docs/review/` 边界。

---

### WO2 — Workspace Layout and RegistryStore Skeleton

目标：建立 workspace boundary 和 SQLite RegistryStore skeleton。

交付物：

```text
aam/workspace/layout.py
aam/workspace/service.py
aam/registry/store.py
aam/registry/schema.py
tests/test_workspace_layout.py
tests/test_registry_store_schema.py
```

任务：

1. 实现 workspace init/open。
2. 创建 `.aam/` layout。
3. 创建 `workspace.json` 或等价 metadata。
4. 实现 `RegistryStore.connect()`。
5. 实现 schema bootstrap skeleton。
6. 写 tests。

验收标准：

- `aam workspace init` 或对应 service 能创建 workspace。
- `.aam/registry.sqlite3` 可以初始化。
- schema version 可查询。
- init 不覆盖已有 workspace。
- 不实现 import / rebuild 业务逻辑。

---

### WO3 — SQLite Schema and Deterministic JSON Codec

目标：实现 registry schema 和 deterministic JSON serialization。

交付物：

```text
aam/registry/migrations.py
aam/registry/json_codec.py
tests/test_registry_schema_bootstrap.py
tests/test_deterministic_json_codec.py
```

任务：

1. 实现 registry_meta。
2. 实现 packages/assets/profiles/cards/dependencies/profile_includes tables。
3. 实现 graph nodes/edges tables。
4. 实现 validation issues table。
5. 实现 event placeholder tables。
6. 实现 deterministic JSON codec。
7. 添加 schema smoke tests。

验收标准：

- 所有 Phase 2 required tables 存在。
- required indexes 存在或有明确 deferred reason。
- JSON codec sort keys、稳定处理 enum/list/dict。
- 不实现 production migration complexity；schema bootstrap 足够 Phase 2。

---

### WO4 — Registry Rebuild Pipeline

目标：实现从 Phase 1 projection 到 SQLite RegistryStore 的完整 rebuild。

交付物：

```text
aam/registry/rebuild.py
tests/test_registry_rebuild.py
```

任务：

1. 复用 Phase 1 parser / validator / registry builder。
2. 将 in-memory projection 转换为 SQLite rows。
3. 在 transaction 中写入 registry tables。
4. 实现 full rebuild。
5. 实现 validation issue persistence。
6. 实现 rollback on failure。
7. 添加 tests。

验收标准：

- valid package 可以 rebuild 到 SQLite。
- packages/assets/profiles/cards/dependencies/graph/issues 均写入。
- invalid package 不产生半写入状态。
- registry 删除后可以 rebuild。
- CLI 不参与业务逻辑。

---

### WO5 — Store-backed Query Services

目标：实现未来 CLI/API/MCP/UI 可复用的查询服务。

交付物：

```text
aam/registry/service.py
aam/registry/query.py
aam/registry/graph_query.py
aam/registry/stats.py
tests/test_registry_query_service.py
tests/test_graph_query_service.py
tests/test_stats_service.py
```

任务：

1. 实现 RegistryService facade。
2. 实现 AssetQueryService。
3. 实现 GraphQueryService。
4. 实现 StatsService。
5. 实现 filters。
6. 实现 dependency / reverse dependency query。
7. 实现 orphan / broken reference summary。
8. 添加 tests。

验收标准：

- 可查询 package / asset / profile / card。
- 可按 type / tag / trust / lifecycle / target_host / source 过滤。
- 可查询 dependencies / reverse dependencies。
- 可输出 graph JSON。
- 可输出 stats summary。
- Query service 不重新解析 manifest。

---

### WO6 — Event Placeholder Store

目标：实现 UsageEvent / AuditLog / RejectionEvent 的最小 append-only store。

交付物：

```text
aam/events/models.py
aam/events/store.py
tests/test_event_placeholder_store.py
```

任务：

1. 定义 common actor model。
2. 定义 UsageEvent。
3. 定义 AuditLog。
4. 定义 RejectionEvent。
5. 实现 append methods。
6. 实现 recent/list query。
7. 添加 tests。

验收标准：

- Events append-only。
- Event rows 包含 workspace_id、occurred_at、actor、target/result/reason metadata。
- RejectionEvent 支持 follow_up_action。
- 不实现 recommendation learning。
- 不实现 full governance workflow。

---

### WO7 — SourceAdapter Interface and ImportRun Model

目标：建立 import service 的通用抽象和报告模型。

交付物：

```text
aam/importing/models.py
aam/importing/source_adapter.py
aam/importing/import_run.py
aam/importing/service.py
tests/test_source_adapter_contract.py
tests/test_import_run_model.py
```

任务：

1. 定义 ImportRequest。
2. 定义 SourceInspection。
3. 定义 DetectedAssetCandidate。
4. 定义 ImportRunReport。
5. 定义 SourceAdapter protocol。
6. 实现 ImportService skeleton。
7. 添加 tests。

验收标准：

- Import model 能表达 local adopt、local copy/snapshot、GitHub import。
- ImportRun report 能表达 warnings/errors/trust default/resolved ref。
- SourceAdapter 不直接写 RegistryStore。
- 不实现具体 adapters，除非 skeleton tests 需要 fake adapter。

---

### WO8 — Local Directory Import

目标：实现 local adopt 和 local copy/snapshot import。

交付物：

```text
aam/importing/local_directory.py
aam/importing/manifest_writer.py
tests/test_local_adopt_import.py
tests/test_local_copy_snapshot_import.py
```

任务：

1. 实现 native package detection。
2. 实现 adopt mode。
3. 实现 copy/snapshot mode。
4. 实现 basic asset detection heuristic。
5. 实现 wrapper manifest generation。
6. 生成 ImportRun report。
7. import 成功后触发或指导 rebuild。
8. 添加 tests。

验收标准：

- Native package adopt 可以进入 workspace registry。
- Unstructured local folder 可以生成 wrapper manifest。
- Copy/snapshot 会复制到 workspace-managed area。
- Imported generated assets 默认 unreviewed / needs_manual_review。
- dry-run 不写文件。
- import failure 不污染 registry。

---

### WO9 — GitHub Public Import v0

目标：实现 GitHub public source import 的最小正式入口。

交付物：

```text
aam/importing/github.py
tests/test_github_import_v0.py
```

任务：

1. 支持 repo URL + ref。
2. 支持 optional path。
3. 将 branch/tag/ref 解析为 commit SHA。
4. 下载或 checkout public source 到 workspace-managed import area。
5. 检测 native package 或生成 wrapper manifest。
6. 记录 source provenance。
7. 生成 ImportRun report。
8. 添加 tests。

验收标准：

- GitHub import pin 到 resolved commit SHA。
- Imported assets 默认 unreviewed / needs_manual_review。
- import report 包含 requested_ref 和 resolved_ref。
- 不支持 private repo auth。
- 不支持 branch auto update。
- 不安装外部依赖。

测试可以使用 mocked GitHub interaction 或本地 fake git repository，避免依赖真实网络。

---

### WO10 — CLI Usability, Docs, and Phase 2 Closeout

目标：把 Phase 2 service 串成可演示 CLI，并完成文档与 closeout。

交付物：

```text
aam/cli/main.py
aam/cli/commands.py
aam/cli/formatters.py
docs/phase2_registry_import_quickstart.md
dev_docs/phase2/phase_2_closeout_checklist.md
tests/test_phase2_cli_smoke.py
```

任务：

1. 实现 workspace CLI。
2. 实现 registry rebuild/stats/issues/graph export CLI。
3. 实现 local import CLI。
4. 实现 GitHub import CLI。
5. 实现 list/show query CLI。
6. 实现 `--json` output。
7. 写 quickstart。
8. 写 closeout checklist。
9. 添加 CLI smoke tests。

验收标准：

- CLI 可以完成 Phase 2 demo workflow。
- JSON output parseable and deterministic。
- Human-readable output 清晰展示 warnings 和 next steps。
- CLI 不直接访问 SQLite rows。
- 文档明确 Phase 2 不包含 API/MCP/UI/Assembly/Lockfile/Materialization。

---

## 20. Acceptance Criteria

Phase 2 完成时必须满足以下标准。

### 20.1 Functional Acceptance

1. 用户可以初始化 AAM workspace。
2. Workspace 下存在 `.aam/registry.sqlite3`。
3. Registry schema 可以初始化。
4. 用户可以 rebuild registry。
5. Registry 可以持久化 packages、assets、profiles、Asset Cards、dependencies、profile includes、graph nodes/edges 和 validation issues。
6. Registry 可删除后重建。
7. Rebuild 失败不会留下半写入 projection。
8. 用户可以查询 assets。
9. 用户可以查询 profiles。
10. 用户可以查询 Asset Card。
11. 用户可以查询 dependencies 和 reverse dependencies。
12. 用户可以查看 stats summary。
13. 用户可以导出 graph JSON。
14. 用户可以查看 validation issues。
15. 用户可以 local adopt import。
16. 用户可以 local copy/snapshot import。
17. 用户可以 GitHub public import。
18. GitHub import pin 到 resolved commit SHA。
19. ImportRun report 可生成并保存。
20. Imported assets 默认不 trusted。
21. UsageEvent / AuditLog / RejectionEvent placeholder 可以 append 和 query。
22. CLI 支持 `--json`。

### 20.2 Architectural Acceptance

1. Manifest 仍然是事实来源。
2. SQLite registry 是可重建 query projection。
3. One workspace one registry DB。
4. RegistryStore 不解析 manifest。
5. Rebuild pipeline 复用 Phase 1 parser / validator / builder。
6. Query services 不重新扫描文件。
7. CLI 调用 service boundary。
8. Import adapters 不直接写 registry rows。
9. ImportRun report 与 source provenance 明确分离。
10. Event placeholders 不变成完整 governance workflow。
11. 没有 production HTTP API。
12. 没有 production MCP Server。
13. 没有 Web UI。
14. 没有 Assembly Plan / Package Lock / Materialization production implementation。

### 20.3 Testing Acceptance

1. Workspace layout 有测试。
2. Registry schema bootstrap 有测试。
3. Deterministic JSON codec 有测试。
4. Registry rebuild 有测试。
5. Rollback behavior 有测试。
6. Query service 有测试。
7. Graph query 有测试。
8. Stats service 有测试。
9. Event placeholder store 有测试。
10. SourceAdapter contract 有测试。
11. Local adopt import 有测试。
12. Local copy/snapshot import 有测试。
13. GitHub import v0 有测试。
14. CLI smoke tests 覆盖主要命令。
15. Snapshot tests 覆盖 stats / graph / import report / JSON outputs。

### 20.4 Demo Acceptance

必须可以执行类似流程：

```bash
aam workspace init ./tmp/aam-workspace

aam import local ./examples/personal-agent-assets \
  --workspace ./tmp/aam-workspace \
  --mode adopt

aam registry rebuild ./tmp/aam-workspace

aam registry stats ./tmp/aam-workspace

aam list assets --workspace ./tmp/aam-workspace

aam show card code-reviewer --workspace ./tmp/aam-workspace --json

aam registry graph export ./tmp/aam-workspace --json
```

GitHub import demo 可以使用 fake local git repo 或 mock-backed test fixture：

```bash
aam import github https://github.com/example/repo \
  --ref main \
  --workspace ./tmp/aam-workspace \
  --dry-run
```

---

## 21. Testing Plan

### 21.1 Unit Tests

Workspace tests:

- init creates `.aam/` layout。
- init does not overwrite existing workspace。
- open missing workspace fails clearly。

Registry schema tests:

- schema tables exist。
- schema version exists。
- required indexes exist or are explicitly deferred。

JSON codec tests:

- dict keys sorted。
- enum serialized as string。
- list order preserved。
- repeated dumps stable。

Rebuild tests:

- valid package rebuilds successfully。
- assets/cards/dependencies/graph written。
- invalid package rollback。
- rebuild after deleting DB succeeds。

Query tests:

- list/get package。
- list/get asset。
- filters。
- get card。
- dependencies。
- reverse dependencies。
- unknown asset error。

Stats tests:

- counts by type/trust/lifecycle/source/target。
- orphan asset detection。
- broken reference summary。

Import tests:

- local native package adopt。
- local unstructured folder wrapper manifest。
- local copy/snapshot writes managed files。
- dry-run writes nothing。
- GitHub ref resolves to commit SHA。
- GitHub generated assets default unreviewed。

Event tests:

- append usage event。
- append audit log。
- append rejection event。
- query recent events。

CLI tests:

- workspace init。
- registry rebuild。
- registry stats `--json`。
- local import dry-run。
- list assets `--json`。
- show card `--json`。
- graph export `--json`。

### 21.2 Fixture Strategy

Required fixtures:

```text
tests/fixtures/phase2/
  workspace_empty/
  valid_single_package_workspace/
  valid_multi_package_workspace/
  local_import_native_package/
  local_import_unstructured_assets/
  local_import_with_risky_mcp_config/
  github_import_native_package_fixture/
  github_import_unstructured_fixture/
  invalid_import_missing_files/
  invalid_import_broken_manifest/
```

### 21.3 Snapshot Tests

Recommended snapshot targets:

```text
registry stats JSON
registry graph export JSON
ImportRun report JSON
AssetQueryService list JSON
Event placeholder JSON
```

Snapshot tests should normalize:

- absolute paths；
- timestamps；
- generated IDs where necessary；
- platform-specific path separators。

---

## 22. Risks and Mitigations

### Risk 1 — SQLite Registry Becomes Source of Truth

问题：实现者可能把 registry 当成主数据源，忽略 manifest/source provenance。

缓解：所有 rebuild 和 import 文档必须强调 registry 是 query projection；editing manifest 不属于 Phase 2。

### Risk 2 — CLI 绕过 Service Layer

问题：CLI 为了省事直接读 SQLite 或扫描文件。

缓解：PR review 必须检查 CLI 是否只调用 RegistryService / ImportService / WorkspaceService。

### Risk 3 — Import Detection 过度智能化

问题：试图自动理解所有 prompts/skills/tools，导致实现失控。

缓解：Phase 2 detection 只做 heuristic candidates；不确定时用 `other` 和 warning。

### Risk 4 — GitHub Import 变成完整同步系统

问题：实现 branch tracking、upgrade diff、private auth、merge workflow。

缓解：Phase 2 只做 public import v0，pin commit SHA；升级与同步后置。

### Risk 5 — Event Placeholder 变成治理系统

问题：实现 recommendation learning、review workflow、governance dashboard。

缓解：Phase 2 只实现 append/query placeholder；完整治理进入 Phase 6/8。

### Risk 6 — Registry Schema 过度规范化

问题：过早拆太多表，拖慢阶段。

缓解：复杂结构使用 deterministic JSON；只规范化高频查询和关系边。

### Risk 7 — Rebuild Incremental Complexity 过早出现

问题：实现复杂增量更新、dirty tracking、watcher。

缓解：Phase 2 优先 full rebuild；package-level rebuild 可选但不得阻塞主线。

### Risk 8 — Phase 3 功能越界

问题：实现 profile closure、assembly planner、lockfile。

缓解：Phase 2 只提供 registry query service 给 Phase 3 使用；组合逻辑后置。

---

## 23. Review Checklist

每个 Phase 2 PR review 时应确认：

- [ ] PR 是否只完成当前 Work Order。
- [ ] 是否遵守 Manifest as source of truth。
- [ ] 是否保持 Registry as query projection。
- [ ] 是否使用 SQLite as workspace-scoped store。
- [ ] 是否没有引入 multi-workspace shared registry。
- [ ] 是否没有实现 production API / MCP / Web UI。
- [ ] 是否没有实现 Profile closure / Assembly Plan / Package Lock / Materialization。
- [ ] 是否没有让 CLI 直接扫描文件或直接访问 SQLite rows。
- [ ] 是否复用 Phase 1 parser / validator / registry builder。
- [ ] 是否保持 deterministic JSON policy。
- [ ] 是否有 rollback / failure path 测试。
- [ ] Import 是否保留 source provenance。
- [ ] GitHub import 是否 pin 到 resolved commit SHA。
- [ ] Imported assets 是否默认不 trusted。
- [ ] Event placeholder 是否 append-only 且没有治理越界。
- [ ] 测试是否覆盖当前 WO 的核心行为。
- [ ] JSON output 是否 parseable。
- [ ] 文档是否更新。

---

## 24. Phase 2 Completion Definition

Phase 2 可以视为完成，当且仅当：

1. WO1-WO10 全部完成并合并。
2. 所有 functional acceptance 通过。
3. 所有 architectural acceptance 通过。
4. 所有 testing acceptance 通过。
5. Phase 2 demo workflow 可以在本地执行。
6. Tests 全部通过。
7. Ruff / lint 通过，如项目已配置。
8. Quickstart 已完成。
9. Closeout checklist 已完成。
10. Codex final review 和 Claude final review 无 unresolved P0/P1。
11. main 上 final verification 通过。
12. 没有引入 Phase 3+ production capability。
13. Phase 3 implementation spec 可以直接基于 Phase 2 QueryService / RegistryService 开写。

完成后建议 tag：

```text
phase-2-persistent-registry-import-service-cli-usability
```

或如果项目开始采用 semver：

```text
v0.2.0
```

---

## 25. Handoff to Phase 3

Phase 2 完成后，Phase 3 应进入：

> Profile Composition, Assembly Plan & Lockfile

Phase 3 不应重新实现 registry query、asset filtering、Asset Card projection、dependency lookup、reverse dependency lookup、stats 或 graph export。

Phase 3 应直接依赖 Phase 2 的：

```text
RegistryService
AssetQueryService
GraphQueryService
StatsService
RegistryStore
EventStore placeholders
```

Phase 3 的核心新增能力应是：

```text
ProfileClosureService
DiscoveryService
AssemblyPlanner
AssemblyPlanValidator
Approval boundary
LockBuilder
MaterializationPreviewService
```

Phase 2 的完成质量决定 Phase 3 能否专注于组合语义，而不是回头补 registry、import 和 query 基础设施。

---

## 26. Summary

Phase 2 的核心价值是把 Agent Asset Management 从“能解析和索引一个 package 的 Phase 1 demo”推进到“可以长期使用的本地 workspace registry”。

本阶段应交付：

```text
workspace
  -> SQLite registry
  -> deterministic rebuild
  -> stable query services
  -> local/GitHub import
  -> ImportRun report
  -> event placeholders
  -> enhanced CLI
```

Phase 2 成功的判断标准不是功能数量，而是边界是否稳定：

> 后续 API、MCP、Web UI、Assembly、Lockfile 和 Materialization 都应该能复用 Phase 2 的 registry 和 import 基座，而不需要重新扫描文件、重建查询模型或重新设计 source provenance。

