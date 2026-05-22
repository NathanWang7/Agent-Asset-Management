# Phase 1 Core Package System MVP Implementation Spec

## 1. Status

Draft v0.1

本文档是 Agent Asset Management 项目的 Phase 1 实施规格文档。

它不是产品简报，也不是长期路线图，而是第一阶段工程实现的执行边界。它的目标是把前置的 Product Brief 与 Foundation & Roadmap Spec 转化为可以交给 Claude Code / Codex / 其他 AI coding agent 执行的阶段级 implementation spec。

Phase 1 的主题是：

> Core Package System MVP

也就是建立 Agent Asset Management 的最小资产包系统，让系统可以描述、校验、索引、查询和展示一个本地 Agent asset package。

本阶段结束后，项目不需要已经具备完整导入、持久化、Web UI、MCP、Profile Assembly 或 materialization 能力；但必须已经具备后续所有阶段依赖的核心数据模型、manifest 规范、validator、content hash、registry projection、Asset Card projection 和 graph-aware 基础关系。

---

## 2. Goal

Phase 1 的目标是完成本项目的最小资产描述、校验和本地索引闭环。

更具体地说，Phase 1 应让用户能够：

1. 创建一个本地 asset package。
2. 在 `package.yaml` 中声明 package、assets 和 profiles。
3. 登记 prompt、agent、skill、instruction、mcp_server、workflow、template、schema 等基础资产类型。
4. 校验 manifest 与文件结构是否自洽。
5. 检测 missing files、broken references、invalid enum values、dependency cycles 等核心错误。
6. 为每个 asset 计算 content hash。
7. 生成最小 Asset Card projection。
8. 构建 in-memory registry。
9. 查询 package、asset、profile 和 dependency 信息。
10. 输出 graph nodes / edges JSON。
11. 通过最小 CLI 执行 `init / validate / index / list / show`。

Phase 1 的工程目标不是“做一个完整产品”，而是建立一个后续 Phase 2-6 都可以依赖的稳定底座。

---

## 3. Core Design Principles Applied in Phase 1

Phase 1 必须落实以下原则。

### 3.1 Manifest as Source of Truth

`package.yaml` 是 package、asset、profile、dependency、visibility、trust、lifecycle、target、permission 和 source metadata 的声明来源。

Registry 是由 manifest、asset files 和计算结果构建出来的查询投影，不是唯一事实源。

### 3.2 Registry as Query Projection

Phase 1 的 registry 可以是 in-memory registry，但其模型边界必须稳定，后续 Phase 2 可以无痛替换为 persistent registry store。

CLI、后续 API、后续 Web UI、后续 MCP Server 不应该各自扫描文件，而应该通过 registry / query service 获取数据。

### 3.3 Asset Card Before Full Content

Asset Card 是外部 Agent 未来读取资产前的安全摘要层。

Phase 1 不需要复杂 LLM 自动摘要，但必须至少能从 manifest 和基础索引结果投影出 Asset Card 的硬字段。

### 3.4 Graph-aware From Day One

即使 Phase 1 不做图谱 UI，也必须生成基础 graph nodes / edges。

至少支持：

- package contains asset
- package contains profile
- profile includes asset
- asset depends on asset
- asset has tag
- asset targets host
- asset imported from source
- asset has trust status
- asset has lifecycle status

### 3.5 Trust Before Automation

Phase 1 不做复杂治理，但必须引入 trust model。

至少需要支持：

- `trusted`
- `unreviewed`
- `sandbox_only`
- `blocked`
- `needs_manual_review`

Validator 和 registry 必须知道 blocked / unreviewed 的存在，后续 assembly 和 materialization 才能执行 policy gate。

### 3.6 Small Core, Extensible Types

Phase 1 不应为每一种 asset type 设计复杂 schema。

核心模型应采用统一 Asset model，并允许 asset type 以后扩展。

---

## 4. Scope

Phase 1 包含以下能力。

### 4.1 Package Directory Convention

定义最小 package 目录约定：

```text
my-agent-package/
  package.yaml
  prompts/
  agents/
  skills/
  instructions/
  workflows/
  schemas/
  templates/
  resources/
```

Phase 1 不强制所有目录必须存在。唯一强制要求是：

```text
package.yaml must exist at package root.
```

Asset path 必须相对 package root。

### 4.2 Manifest Schema

支持 `package.yaml` 的最小 manifest schema：

```yaml
package:
  id: string
  name: string
  version: string
  description: string | null
  tags: list[string]
  source:
    kind: manual_created | local_directory | github_repository | unknown
    original_location: string | null
    resolved_ref: string | null

assets:
  - id: string
    type: prompt | agent | skill | tool | mcp_server | workflow | instruction | knowledge | eval_case | template | schema | host_instruction_pack | other
    path: string
    visibility: internal | exported | shared
    lifecycle_status: draft | active | deprecated | archived
    trust_status: trusted | unreviewed | sandbox_only | blocked | needs_manual_review
    description: string | null
    tags: list[string]
    depends_on: list[string]
    target_hosts: list[string]
    permissions:
      filesystem: none | read | write | broad
      network: none | read | broad
      shell: none | limited | broad
    context_cost:
      estimated_tokens: int | null
    agent_card:
      title: string | null
      summary: string | null
      intended_use: list[string]
      input_context: dict
      output_capabilities: list[string]
      risk_level: low | medium | high | unknown
    metadata: dict

profiles:
  - id: string
    target_host: string
    description: string | null
    includes: list[string]
    tags: list[string]
```

### 4.3 Typed Domain Models

实现以下 typed models：

- `PackageManifest`
- `PackageInfo`
- `AssetManifest`
- `ProfileManifest`
- `AssetCardManifest`
- `AssetCardProjection`
- `SourceProvenance`
- `PermissionSpec`
- `ContextCostSpec`
- `IndexedPackage`
- `IndexedAsset`
- `IndexedProfile`
- `InMemoryRegistry`
- `GraphNode`
- `GraphEdge`
- `GraphProjection`
- `ValidationIssue`
- `ValidationReport`

### 4.4 Enums and Constants

实现以下 enums：

```text
AssetType
AssetVisibility
LifecycleStatus
TrustStatus
FilesystemPermission
NetworkPermission
ShellPermission
RiskLevel
SourceKind
GraphNodeType
GraphEdgeType
ValidationSeverity
```

### 4.5 Manifest Parser

实现 manifest parser：

- 读取 `package.yaml`。
- 解析 YAML。
- 映射为 typed models。
- 保留字段校验错误。
- 禁止 silent ignore 关键错误。
- 对可选字段应用明确默认值。

### 4.6 Validator

实现 package validator：

- `package.id` 必须存在。
- `package.version` 必须存在。
- asset id 在同 package 内唯一。
- profile id 在同 package 内唯一。
- asset path 必须存在，除非 asset type 未来显式允许 virtual asset。Phase 1 默认不支持 virtual asset。
- `depends_on` 引用必须可解析。
- `profile.includes` 引用必须可解析。
- `visibility`、`trust_status`、`lifecycle_status`、`permissions`、`risk_level` 必须是合法枚举。
- dependency graph 不能有 cycle。
- blocked asset 可以存在，但 validator 应产生 warning：blocked asset will not be usable in future assembly/materialization。
- unreviewed asset 可以存在，但 validator 应产生 warning：unreviewed asset requires explicit warning in future assembly/materialization。
- archived asset 可以存在，但 validator 应产生 info/warning：archived asset should not participate in new plans by default。

### 4.7 Reference Resolver

实现统一 reference resolver。

Phase 1 最小支持以下引用格式：

```text
asset:<asset_id>
<asset_id>
```

其中：

- `<asset_id>` 是同 package 内简写。
- `asset:<asset_id>` 是推荐显式格式。

Phase 1 可以解析但不完全启用以下未来格式：

```text
asset:<package_id>/<asset_id>
asset:<package_id>/<asset_id>@<version>
```

对跨 package 引用，Phase 1 应返回 explicit unsupported warning，而不是 silently accept。

### 4.8 Content Hash

实现 asset content hash：

- 使用 SHA-256。
- 对 asset file bytes 计算 hash。
- hash 格式为 `sha256:<hex>`。
- hash 存入 `IndexedAsset.content_hash`。
- Phase 1 不要求把 hash 写回 manifest。

### 4.9 Asset Card Projection

从 manifest 和 indexed asset 生成最小 Asset Card projection。

Phase 1 必须包含以下硬字段：

```text
id
package_id
version
type
title
summary
tags
target_hosts
dependencies
trust_status
lifecycle_status
visibility
permissions
risk_level
estimated_context_cost
content_hash
source
```

字段来源规则：

- `title` 优先来自 `agent_card.title`，缺失时 fallback 到 asset id。
- `summary` 优先来自 `agent_card.summary`，缺失时 fallback 到 `description`，再缺失则为空。
- `dependencies` 来自 `depends_on` 解析结果。
- `trust_status` 必须来自 manifest，不允许自动推断为 trusted。
- `permissions` 必须来自 manifest default 或显式声明，不允许由内容质量推断。
- `risk_level` 优先来自 manifest；缺失时为 `unknown`。

Phase 1 不做 LLM 摘要生成。

### 4.10 In-memory Registry

实现 in-memory registry builder。

输入：

```text
package root path
parsed manifest
validation report
content hash results
asset card projections
```

输出：

```text
InMemoryRegistry
  packages
  assets
  profiles
  asset_cards
  dependencies
  reverse_dependencies
  graph_projection
```

Registry 必须支持查询：

- list packages
- get package
- list assets
- get asset
- list profiles
- get profile
- get asset card
- get dependencies
- get reverse dependencies
- filter assets by type / tag / trust / lifecycle / target_host

### 4.11 Graph Projection

实现 graph projection。

Phase 1 的 graph projection 是轻量数据投影，不是完整图谱系统。实现目标是证明 registry 已经保留足够的关系信息，并能稳定输出 deterministic JSON；不得在本阶段投入过多精力完善 graph ontology、layout、交互、诊断算法或复杂 node / edge 类型体系。

最小 node types：

```text
package
asset
profile
tag
target_host
source
trust_status
lifecycle_status
```

最小 edge types：

```text
package_contains_asset
package_contains_profile
profile_includes_asset
asset_depends_on_asset
asset_has_tag
profile_has_tag
asset_targets_host
asset_imported_from_source
asset_has_trust_status
asset_has_lifecycle_status
```

Graph projection 应能输出 JSON：

```json
{
  "nodes": [],
  "edges": []
}
```

### 4.12 Minimal CLI

实现最小 CLI：

```bash
aam init <package-dir>
aam validate <package-dir>
aam index <package-dir> [--json]
aam list assets <package-dir> [--json]
aam list profiles <package-dir> [--json]
aam show asset <package-dir> <asset-id> [--json]
aam show card <package-dir> <asset-id> [--json]
aam graph export <package-dir> [--json]
```

CLI 可以在后续阶段调整命令细节，但 Phase 1 应至少提供可演示闭环。

### 4.13 Fixtures and Examples

至少提供以下 fixtures：

```text
fixtures/
  valid_basic_package/
  invalid_missing_file/
  invalid_broken_dependency/
  invalid_cycle/
  valid_unreviewed_import_like_package/
  valid_blocked_asset_package/
```

每个 fixture 应包含：

- `package.yaml`
- 对应 asset files
- README 或测试说明

---

## 5. Non-goals

Phase 1 明确不做以下内容：

1. 不做 GitHub importer。
2. 不做 LocalDirectorySourceAdapter 的正式导入 workflow。
3. 不做 ImportRun 持久化。
4. 不做 persistent registry DB。
5. 不做 SQLite / DuckDB storage。
6. 不做 HTTP API。
7. 不做 MCP Server。
8. 不做 Web UI。
9. 不做 Profile closure 的完整 materialization。
10. 不做 Assembly Plan。
11. 不做 Package Lock。
12. 不做 target-specific adapters。
13. 不做 full content access policy。
14. 不做 Package Lock、lock-specific hash、policy snapshot 或 lockfile schema。
15. 不做 rejection event 持久化。
16. 不做 asset editing。
17. 不做 review form。
18. 不做 semantic search。
19. 不做 dashboard。
20. 不做 graph visualization UI。
21. 不做 team workspace。

Phase 1 允许为这些能力预留字段和接口，但不得把这些能力的完整实现塞入本阶段。

---

## 6. Proposed Package Layout

建议第一阶段采用以下 Python package 结构：

```text
aam/
  __init__.py

  core/
    __init__.py
    enums.py
    errors.py
    paths.py

  models/
    __init__.py
    manifest.py
    indexed.py
    asset_card.py
    graph.py
    validation.py

  manifest/
    __init__.py
    parser.py
    defaults.py
    resolver.py
    validator.py

  registry/
    __init__.py
    builder.py
    service.py
    query.py

  graph/
    __init__.py
    projection.py

  hash/
    __init__.py
    content_hash.py

  cli/
    __init__.py
    main.py
    commands.py
    formatters.py

tests/
  fixtures/
  test_manifest_parser.py
  test_manifest_validator.py
  test_reference_resolver.py
  test_content_hash.py
  test_registry_builder.py
  test_registry_query.py
  test_asset_card_projection.py
  test_graph_projection.py
  test_cli_smoke.py
```

说明：

- `models/manifest.py` 存放 manifest source models。
- `models/indexed.py` 存放 registry projection models。
- `models/asset_card.py` 存放 Asset Card projection models。
- `models/graph.py` 存放 graph node / edge models。
- `manifest/parser.py` 只负责读取和解析。
- `manifest/validator.py` 负责语义校验。
- `manifest/resolver.py` 负责 asset reference 解析。
- `registry/builder.py` 负责从 package root 构建 registry。
- `registry/service.py` 提供稳定查询服务。
- `graph/projection.py` 负责从 registry 生成 graph projection。
- `cli/` 只调用 service，不直接实现业务逻辑。

---

## 7. Data Models

### 7.1 PackageInfo

```python
class PackageInfo(BaseModel):
    id: str
    name: str
    version: str
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    source: SourceProvenance = Field(default_factory=SourceProvenance.unknown)
```

### 7.2 SourceProvenance

```python
class SourceProvenance(BaseModel):
    kind: SourceKind = SourceKind.UNKNOWN
    original_location: str | None = None
    resolved_ref: str | None = None
```

Phase 1 不解析 GitHub ref，只保留字段。

### 7.3 AssetManifest

```python
class AssetManifest(BaseModel):
    id: str
    type: AssetType
    path: str
    visibility: AssetVisibility = AssetVisibility.INTERNAL
    lifecycle_status: LifecycleStatus = LifecycleStatus.DRAFT
    trust_status: TrustStatus = TrustStatus.UNREVIEWED
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    target_hosts: list[str] = Field(default_factory=list)
    permissions: PermissionSpec = Field(default_factory=PermissionSpec.default)
    context_cost: ContextCostSpec = Field(default_factory=ContextCostSpec)
    agent_card: AssetCardManifest = Field(default_factory=AssetCardManifest)
    metadata: dict[str, Any] = Field(default_factory=dict)
```

### 7.4 ProfileManifest

```python
class ProfileManifest(BaseModel):
    id: str
    target_host: str
    description: str | None = None
    includes: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
```

### 7.5 PackageManifest

```python
class PackageManifest(BaseModel):
    package: PackageInfo
    assets: list[AssetManifest] = Field(default_factory=list)
    profiles: list[ProfileManifest] = Field(default_factory=list)
```

### 7.6 PermissionSpec

```python
class PermissionSpec(BaseModel):
    filesystem: FilesystemPermission = FilesystemPermission.NONE
    network: NetworkPermission = NetworkPermission.NONE
    shell: ShellPermission = ShellPermission.NONE
```

### 7.7 ContextCostSpec

```python
class ContextCostSpec(BaseModel):
    estimated_tokens: int | None = None
```

### 7.8 AssetCardManifest

```python
class AssetCardManifest(BaseModel):
    title: str | None = None
    summary: str | None = None
    intended_use: list[str] = Field(default_factory=list)
    input_context: dict[str, Any] = Field(default_factory=dict)
    output_capabilities: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.UNKNOWN
```

### 7.9 AssetCardProjection

```python
class AssetCardProjection(BaseModel):
    id: str
    package_id: str
    version: str
    type: AssetType
    title: str
    summary: str | None
    intended_use: list[str]
    input_context: dict[str, Any]
    output_capabilities: list[str]
    tags: list[str]
    target_hosts: list[str]
    dependencies: list[str]
    trust_status: TrustStatus
    lifecycle_status: LifecycleStatus
    visibility: AssetVisibility
    permissions: PermissionSpec
    risk_level: RiskLevel
    estimated_context_cost: int | None
    content_hash: str
    source: SourceProvenance
```

### 7.10 IndexedAsset

```python
class IndexedAsset(BaseModel):
    package_id: str
    package_version: str
    id: str
    qualified_id: str
    type: AssetType
    path: str
    absolute_path: str
    visibility: AssetVisibility
    lifecycle_status: LifecycleStatus
    trust_status: TrustStatus
    description: str | None
    tags: list[str]
    depends_on: list[str]
    resolved_dependencies: list[str]
    target_hosts: list[str]
    permissions: PermissionSpec
    context_cost: ContextCostSpec
    content_hash: str
    source: SourceProvenance
    asset_card: AssetCardProjection
```

`qualified_id` 的 Phase 1 格式：

```text
<package_id>:<asset_id>@<package_version>
```

### 7.11 IndexedProfile

```python
class IndexedProfile(BaseModel):
    package_id: str
    package_version: str
    id: str
    qualified_id: str
    target_host: str
    description: str | None
    includes: list[str]
    resolved_includes: list[str]
    tags: list[str]
```

### 7.12 InMemoryRegistry

```python
class InMemoryRegistry(BaseModel):
    packages: dict[str, IndexedPackage]
    assets: dict[str, IndexedAsset]
    profiles: dict[str, IndexedProfile]
    dependencies: dict[str, list[str]]
    reverse_dependencies: dict[str, list[str]]
    graph: GraphProjection
    validation_report: ValidationReport
```

### 7.13 ValidationIssue

```python
class ValidationIssue(BaseModel):
    severity: ValidationSeverity
    code: str
    message: str
    path: str | None = None
    asset_id: str | None = None
    profile_id: str | None = None
```

### 7.14 ValidationReport

```python
class ValidationReport(BaseModel):
    package_id: str | None = None
    ok: bool
    issues: list[ValidationIssue]
```

---

## 8. Public Interfaces

### 8.1 Python Service Boundary

Phase 1 应提供稳定 Python service boundary。

```python
parse_manifest(package_root: Path) -> PackageManifest
validate_package(package_root: Path, manifest: PackageManifest) -> ValidationReport
build_registry(package_root: Path) -> InMemoryRegistry
```

建议进一步封装：

```python
class RegistryService:
    @classmethod
    def from_package_root(cls, package_root: Path) -> RegistryService: ...

    def list_assets(self, filters: AssetFilters | None = None) -> list[IndexedAsset]: ...
    def get_asset(self, asset_id: str) -> IndexedAsset: ...
    def get_asset_card(self, asset_id: str) -> AssetCardProjection: ...
    def list_profiles(self) -> list[IndexedProfile]: ...
    def get_profile(self, profile_id: str) -> IndexedProfile: ...
    def get_dependencies(self, asset_id: str) -> list[IndexedAsset]: ...
    def get_reverse_dependencies(self, asset_id: str) -> list[IndexedAsset]: ...
    def export_graph(self) -> GraphProjection: ...
```

### 8.2 CLI Interface

#### `aam init`

```bash
aam init ./my-agent-package
```

Expected behavior:

- 创建 package directory，如果不存在。
- 写入最小 `package.yaml`。
- 创建基础目录。
- 不覆盖已有 `package.yaml`，除非显式 `--force`。Phase 1 可先不支持 `--force`。

#### `aam validate`

```bash
aam validate ./my-agent-package
```

Expected behavior:

- 解析 manifest。
- 执行 validator。
- 打印 issues。
- 如果存在 error，exit code 非 0。
- warning 不导致失败。

#### `aam index`

```bash
aam index ./my-agent-package --json
```

Expected behavior:

- 每次调用都从 package root 重新解析 manifest、校验文件、计算 hash，并构建一次临时 in-memory registry。
- 不启动 daemon。
- 不写入 persistent registry。
- 不维护长期 index cache。
- 输出 package / asset / profile 数量。
- JSON mode 输出 registry summary。
- Phase 2 引入 persistent registry 后，`aam index` 的语义可以演进为 rebuild / refresh persistent registry，但 Phase 1 只表示一次性构建和摘要输出。

#### `aam list assets`

```bash
aam list assets ./my-agent-package
```

支持可选 filters：

```bash
--type skill
--tag coding
--trust trusted
--lifecycle active
--target-host codex
--json
```

#### `aam show asset`

```bash
aam show asset ./my-agent-package skill.polars-debugger
```

Expected behavior:

- 输出 asset metadata。
- 输出 content hash。
- 输出 dependencies / reverse dependencies。
- 不默认输出完整文件内容。

#### `aam show card`

```bash
aam show card ./my-agent-package skill.polars-debugger --json
```

Expected behavior:

- 输出 Asset Card projection。

#### `aam graph export`

```bash
aam graph export ./my-agent-package --json
```

Expected behavior:

- 输出 graph nodes / edges JSON。

---

## 9. Validation Rules

### 9.1 Error Rules

以下规则失败时应产生 `error`：

1. `package.yaml` 不存在。
2. YAML 无法解析。
3. required fields 缺失。
4. enum value 非法。
5. asset id 重复。
6. profile id 重复。
7. asset path 不存在。
8. `depends_on` 引用不存在。
9. `profile.includes` 引用不存在。
10. dependency cycle。
11. asset path 指向 package root 外部路径。

### 9.2 Warning Rules

以下规则失败或触发时应产生 `warning`：

1. asset description 为空。
2. Asset Card title / summary 均为空。
3. asset target_hosts 为空。
4. asset trust_status 为 `unreviewed`。
5. asset trust_status 为 `blocked`。
6. asset lifecycle_status 为 `archived`。
7. permissions 中 network / shell / filesystem broad。
8. estimated context cost 为空。
9. source kind 为 unknown。
10. 使用未来跨 package reference 格式。

### 9.3 Info Rules

以下情况可产生 `info`：

1. package 没有 profiles。
2. asset 没有 dependencies。
3. profile 没有 tags。
4. package tags 为空。

---

## 10. Reference Resolution

### 10.1 Supported References in Phase 1

Phase 1 支持同 package reference：

```text
asset:<asset_id>
<asset_id>
```

解析结果为：

```text
<package_id>:<asset_id>@<package_version>
```

### 10.2 Reserved Future References

Phase 1 应识别但不启用：

```text
asset:<package_id>/<asset_id>
asset:<package_id>/<asset_id>@<version>
```

行为：

- validator 产生 warning 或 unsupported error，具体取决于是否被 profile / depends_on 实际使用。
- 不应静默解析为本地 asset。

### 10.3 Dependency Cycle Detection

对 asset dependency graph 执行 cycle detection。

示例：

```text
asset:a -> asset:b -> asset:c -> asset:a
```

应报告：

```text
ERROR DEPENDENCY_CYCLE: asset:a -> asset:b -> asset:c -> asset:a
```

---

## 11. Graph Projection Contract

### 11.1 GraphNode

```python
class GraphNode(BaseModel):
    id: str
    type: GraphNodeType
    label: str
    metadata: dict[str, Any] = Field(default_factory=dict)
```

### 11.2 GraphEdge

```python
class GraphEdge(BaseModel):
    id: str
    type: GraphEdgeType
    source: str
    target: str
    metadata: dict[str, Any] = Field(default_factory=dict)
```

### 11.3 Node ID Convention

Recommended node id formats:

```text
package:<package_id>
asset:<package_id>:<asset_id>@<version>
profile:<package_id>:<profile_id>@<version>
tag:<tag>
target_host:<target_host>
source:<source_kind>:<hash-or-location>
trust_status:<status>
lifecycle_status:<status>
```

### 11.4 Edge ID Convention

Recommended edge id format:

```text
<edge_type>:<source_node_id>-><target_node_id>
```

Edge ids must be deterministic.

### 11.5 Minimum Graph JSON Example

```json
{
  "nodes": [
    {
      "id": "package:my-assets",
      "type": "package",
      "label": "My Assets",
      "metadata": {"version": "0.1.0"}
    },
    {
      "id": "asset:my-assets:code-reviewer@0.1.0",
      "type": "asset",
      "label": "code-reviewer",
      "metadata": {"asset_type": "agent"}
    }
  ],
  "edges": [
    {
      "id": "package_contains_asset:package:my-assets->asset:my-assets:code-reviewer@0.1.0",
      "type": "package_contains_asset",
      "source": "package:my-assets",
      "target": "asset:my-assets:code-reviewer@0.1.0",
      "metadata": {}
    }
  ]
}
```

---

## 12. Example Manifest

```yaml
package:
  id: personal-agent-assets
  name: Personal Agent Assets
  version: 0.1.0
  description: Personal reusable agent assets for AI coding workflows.
  tags:
    - personal
    - coding
  source:
    kind: manual_created
    original_location: null
    resolved_ref: null

assets:
  - id: code-reviewer
    type: agent
    path: agents/code_reviewer.md
    visibility: exported
    lifecycle_status: active
    trust_status: trusted
    description: Reviews code for correctness, maintainability, and risk.
    tags:
      - coding
      - review
    depends_on:
      - asset:coding-style-guide
    target_hosts:
      - codex
      - claude_code
    permissions:
      filesystem: read
      network: none
      shell: none
    context_cost:
      estimated_tokens: 1200
    agent_card:
      title: Code Reviewer
      summary: Reviews code changes and identifies correctness, maintainability, and safety issues.
      intended_use:
        - review code diff
        - identify risky changes
        - suggest safer implementation
      input_context:
        expects:
          - source code
          - diff
          - error logs
      output_capabilities:
        - review comments
        - risk summary
        - improvement suggestions
      risk_level: low
    metadata: {}

  - id: coding-style-guide
    type: instruction
    path: instructions/coding_style.md
    visibility: exported
    lifecycle_status: active
    trust_status: trusted
    description: Shared coding style and implementation principles.
    tags:
      - coding
      - style
    depends_on: []
    target_hosts:
      - codex
      - claude_code
    permissions:
      filesystem: none
      network: none
      shell: none
    context_cost:
      estimated_tokens: 900
    agent_card:
      title: Coding Style Guide
      summary: Defines preferred coding style and implementation constraints.
      intended_use:
        - guide implementation
        - keep code consistent
      input_context: {}
      output_capabilities:
        - coding guidance
      risk_level: low
    metadata: {}

profiles:
  - id: coding-review
    target_host: codex
    description: Baseline profile for coding review tasks.
    includes:
      - asset:code-reviewer
      - asset:coding-style-guide
    tags:
      - coding
      - review
```

---

## 13. Work Orders

Phase 1 应拆成以下 work orders。每个 work order 都应该能独立开 issue / branch / PR。

### Work Order 1 — Project Skeleton and Tooling

Goal:

建立 Python package skeleton、测试框架、CLI 入口和基础 CI。

Tasks:

1. 创建 package layout。
2. 配置 pyproject。
3. 配置 pytest。
4. 配置 ruff / formatting。
5. 创建 `aam` CLI placeholder。
6. 添加 empty smoke test。

Deliverables:

- package skeleton
- CLI entrypoint
- test baseline
- lint baseline

Acceptance Criteria:

- `pytest` 可以运行。
- `aam --help` 可以执行。
- CI baseline 可以运行。

---

### Work Order 2 — Core Enums and Manifest Models

Goal:

实现 manifest typed models 与 enums。

Tasks:

1. 实现 enums。
2. 实现 `SourceProvenance`。
3. 实现 `PermissionSpec`。
4. 实现 `ContextCostSpec`。
5. 实现 `AssetCardManifest`。
6. 实现 `PackageInfo`、`AssetManifest`、`ProfileManifest`、`PackageManifest`。
7. 设置默认值。
8. 添加 model tests。

Deliverables:

- `aam/core/enums.py`
- `aam/models/manifest.py`
- model unit tests

Acceptance Criteria:

- 合法 manifest dict 可以解析为 typed model。
- 非法 enum value 会失败。
- 默认值符合 Phase 1 spec。

---

### Work Order 3 — Manifest Parser and Fixtures

Goal:

实现 `package.yaml` parser 与基础 fixtures。

Tasks:

1. 实现 YAML reader。
2. 实现 parser error handling。
3. 创建 valid basic fixture。
4. 创建 invalid YAML fixture。
5. 创建 missing required field fixture。
6. 添加 parser tests。

Deliverables:

- `aam/manifest/parser.py`
- fixtures
- parser tests

Acceptance Criteria:

- parser 能读取 valid fixture。
- parser 能对 invalid YAML 返回明确错误。
- parser 不吞掉关键错误。

---

### Work Order 4 — Reference Resolver and Validator

Goal:

实现核心 validator 与 reference resolver。

Tasks:

1. 实现 asset id uniqueness check。
2. 实现 profile id uniqueness check。
3. 实现 asset path existence check。
4. 实现 asset path package-boundary check。
5. 实现 `depends_on` resolver。
6. 实现 `profile.includes` resolver。
7. 实现 cycle detection。
8. 实现 warnings for unreviewed / blocked / archived / broad permissions。
9. 添加 validator fixtures。
10. 添加 validator tests。

Deliverables:

- `aam/manifest/resolver.py`
- `aam/manifest/validator.py`
- validation models
- validator tests

Acceptance Criteria:

- missing file 被识别。
- broken dependency 被识别。
- broken profile include 被识别。
- dependency cycle 被识别。
- unreviewed / blocked asset 产生 warning。

---

### Work Order 5 — Content Hash and Asset Card Projection

Goal:

实现 content hash 与 Asset Card projection。

Tasks:

1. 实现 SHA-256 content hash。
2. 实现 asset card projection builder。
3. 实现 title / summary fallback。
4. 实现 dependencies projection。
5. 实现 permissions / trust / lifecycle / context cost projection。
6. 添加 tests。

Deliverables:

- `aam/hash/content_hash.py`
- `aam/models/asset_card.py`
- asset card projection builder
- tests

Acceptance Criteria:

- content hash 稳定。
- Asset Card projection 包含所有 Phase 1 硬字段。
- trust 和 permissions 不被自动推断。

---

### Work Order 6 — In-memory Registry Builder

Goal:

实现从 package root 到 in-memory registry 的完整构建流程。

Tasks:

1. 实现 `IndexedPackage`。
2. 实现 `IndexedAsset`。
3. 实现 `IndexedProfile`。
4. 实现 `InMemoryRegistry`。
5. 集成 parser / validator / hash / card projection。
6. 构建 dependencies / reverse_dependencies。
7. 添加 registry builder tests。

Deliverables:

- `aam/models/indexed.py`
- `aam/registry/builder.py`
- registry tests

Acceptance Criteria:

- valid package 可以构建 registry。
- registry 包含 package / assets / profiles / dependencies / reverse dependencies。
- validation errors 会阻止成功 index，除非 CLI 显式允许后续扩展。

---

### Work Order 7 — Registry Query Service

Goal:

实现稳定查询服务。

Tasks:

1. 实现 `RegistryService`。
2. 实现 list / get package。
3. 实现 list / get asset。
4. 实现 list / get profile。
5. 实现 get asset card。
6. 实现 dependency / reverse dependency query。
7. 实现 asset filters。
8. 添加 query tests。

Deliverables:

- `aam/registry/service.py`
- `aam/registry/query.py`
- query tests

Acceptance Criteria:

- 可按 type / tag / trust / lifecycle / target_host 过滤 asset。
- 查询不存在 asset 时返回明确错误。
- service 不直接重新解析业务逻辑。

---

### Work Order 8 — Graph Projection

Goal:

实现 graph nodes / edges projection。

Tasks:

1. 实现 graph models。
2. 实现 node id convention。
3. 实现 deterministic edge id。
4. 生成 package / asset / profile / tag / target / source / trust / lifecycle nodes。
5. 生成 required edge types。
6. 添加 graph projection tests。

Deliverables:

- `aam/models/graph.py`
- `aam/graph/projection.py`
- graph tests

Acceptance Criteria:

- graph JSON 可稳定输出。
- graph nodes / edges deterministic。
- profile includes、asset depends_on、asset tags、target_hosts 都进入 graph。

---

### Work Order 9 — CLI MVP

Goal:

实现最小 CLI。

Tasks:

1. 实现 `aam init`。
2. 实现 `aam validate`。
3. 实现 `aam index`。
4. 实现 `aam list assets`。
5. 实现 `aam list profiles`。
6. 实现 `aam show asset`。
7. 实现 `aam show card`。
8. 实现 `aam graph export`。
9. 实现 human-readable output。
10. 实现 `--json` output。
11. 添加 CLI smoke tests。

Deliverables:

- `aam/cli/main.py`
- `aam/cli/commands.py`
- `aam/cli/formatters.py`
- CLI tests

Acceptance Criteria:

- CLI 能基于 fixture 跑完整流程。
- JSON 输出可被测试断言。
- `validate` 对 error 返回非 0 exit code。

---

### Work Order 10 — Quickstart and Phase 1 Demo

Goal:

提供 Phase 1 使用文档和可演示流程。

Tasks:

1. 写 quickstart。
2. 写 example package 说明。
3. 写 CLI demo workflow。
4. 写 Phase 1 limitations。
5. 写下一阶段准备说明。

Deliverables:

- `docs/phase1_quickstart.md`
- `examples/personal-agent-assets/`
- demo commands

Acceptance Criteria:

- 用户可以按 quickstart 创建 package、validate、list、show card、export graph。
- 文档明确 Phase 1 不包含 import / API / MCP / UI。

---

## 14. Acceptance Criteria

Phase 1 完成时必须满足以下标准。

### 14.1 Functional Acceptance

1. 用户可以创建一个 package skeleton。
2. 用户可以编写一个包含 assets 和 profiles 的 `package.yaml`。
3. 系统可以解析 manifest。
4. 系统可以校验 manifest 与 asset files。
5. 系统可以报告 missing file。
6. 系统可以报告 broken dependency。
7. 系统可以报告 broken profile include。
8. 系统可以报告 dependency cycle。
9. 系统可以计算每个 asset 的 content hash。
10. 系统可以生成 Asset Card projection。
11. 系统可以构建 in-memory registry。
12. 系统可以查询 asset list。
13. 系统可以查看单个 asset metadata。
14. 系统可以查看单个 Asset Card。
15. 系统可以查看 dependencies / reverse dependencies。
16. 系统可以输出 graph nodes / edges JSON。
17. CLI 可以完成 init / validate / index / list / show / graph export。

### 14.2 Architectural Acceptance

1. Manifest model 与 indexed model 分离。
2. Parser、validator、registry builder、query service、graph projection 分离。
3. CLI 不直接扫描文件实现业务逻辑。
4. Registry 可以后续替换为 persistent store。
5. Asset Card projection 不依赖外部 LLM。
6. Trust status、lifecycle status、visibility、permissions、source provenance、content hash 均进入 registry。
7. Graph projection 从 registry 生成，而不是维护另一份人工图谱。
8. Reference resolver 明确保留未来跨 package reference 格式。

### 14.3 Testing Acceptance

1. Parser 有测试。
2. Validator 有测试。
3. Reference resolver 有测试。
4. Cycle detection 有测试。
5. Content hash 有测试。
6. Asset Card projection 有测试。
7. Registry builder 有测试。
8. Registry query service 有测试。
9. Graph projection 有测试。
10. CLI smoke tests 覆盖主要命令。
11. 至少 6 个 fixtures 覆盖正常和错误场景。

### 14.4 Demo Acceptance

必须可以执行类似流程：

```bash
aam init ./examples/personal-agent-assets
aam validate ./examples/personal-agent-assets
aam index ./examples/personal-agent-assets
aam list assets ./examples/personal-agent-assets
aam show asset ./examples/personal-agent-assets code-reviewer
aam show card ./examples/personal-agent-assets code-reviewer --json
aam graph export ./examples/personal-agent-assets --json
```

---

## 15. Testing Plan

### 15.1 Unit Tests

Parser tests:

- valid manifest parses successfully。
- missing package section fails。
- invalid enum fails。
- default values are applied。

Validator tests:

- missing asset file。
- duplicate asset id。
- duplicate profile id。
- broken depends_on。
- broken profile includes。
- dependency cycle。
- blocked / unreviewed warnings。
- path escaping package root fails。

Reference resolver tests:

- resolves `<asset_id>`。
- resolves `asset:<asset_id>`。
- identifies future cross-package reference。
- rejects unknown asset。

Hash tests:

- same file produces same hash。
- changed file produces different hash。
- hash format starts with `sha256:`。

Asset Card tests:

- title fallback。
- summary fallback。
- trust status preserved。
- permissions preserved。
- dependencies projected。

Registry tests:

- builds registry from valid package。
- dependencies and reverse dependencies are correct。
- filters work。
- get unknown asset fails clearly。

Graph tests:

- required nodes are generated。
- required edges are generated。
- graph output deterministic。

CLI tests:

- `aam --help`。
- `aam validate valid_package` returns 0。
- `aam validate invalid_package` returns non-zero。
- `aam show card --json` returns valid JSON。
- `aam graph export --json` returns valid graph JSON。

### 15.2 Fixture Strategy

Fixtures should be small but semantically meaningful。

Required fixtures:

```text
valid_basic_package
invalid_missing_file
invalid_broken_dependency
invalid_broken_profile_include
invalid_cycle
valid_unreviewed_import_like_package
valid_blocked_asset_package
invalid_path_escape
```

### 15.3 Snapshot Tests

Recommended snapshot targets:

- Asset Card JSON。
- Registry summary JSON。
- Graph projection JSON。

Snapshot tests should avoid absolute paths where possible, or normalize paths before assertion。

---

## 16. Risks and Mitigations

### Risk 1 — Manifest Schema Becomes Too Heavy

Problem:

Phase 1 如果把所有未来能力都塞入 manifest，会导致第一阶段实现过重。

Mitigation:

只实现通用 Asset model 和核心字段。复杂 asset-type-specific schema 后置。

### Risk 2 — Registry Model Too Narrow

Problem:

如果 registry 只服务 CLI list/show，后续 API、MCP、UI、Graph 会返工。

Mitigation:

Phase 1 registry 必须包含 trust、lifecycle、visibility、permissions、source、content_hash、Asset Card 和 graph relations。

### Risk 3 — CLI Coupled to Parser Internals

Problem:

CLI 如果直接读 manifest，会导致后续 API/MCP 重复逻辑。

Mitigation:

CLI 只能调用 `RegistryService` / `build_registry` / `validate_package` 等 service boundary。

### Risk 4 — Asset Card 被误做成 LLM Summary

Problem:

早期如果依赖 LLM 自动总结，会引入不稳定性和安全问题。

Mitigation:

Phase 1 Asset Card 仅做 deterministic projection。LLM summary 后置。

### Risk 5 — Graph Projection 过早复杂化

Problem:

如果 Phase 1 做复杂 graph layout，会拖慢核心系统。

Mitigation:

Phase 1 只输出 graph JSON，不做 visualization，不做 layout。

### Risk 6 — Cross-package Dependency Premature Complexity

Problem:

跨 package dependency 会引入 registry scope、version resolution 和 visibility policy。

Mitigation:

Phase 1 只支持同 package references；识别未来格式但不正式启用。

### Risk 7 — Trust Policy 被 Validator 误当成硬错误

Problem:

unreviewed / blocked 是合法状态，不应导致 manifest 无法解析。

Mitigation:

Validator 对 blocked / unreviewed 产生 warning，不把它们当 schema error。真正 policy gate 在 Phase 3+。

### Risk 8 — Package Lock 过早侵入 Phase 1

Problem:

Foundation 将 Package Lock 定义为后续复现边界，但如果 Phase 1 过早引入 lockfile schema、policy snapshot 或 lock-specific hash，会把 Core Package System MVP 变成组合与发布系统，导致阶段失焦。

Mitigation:

Phase 1 只保留 Package Lock 未来所需的基础输入：asset stable id、package version、content hash、source provenance、trust status、visibility、permissions、target_hosts 和 dependency relations。Package Lock、policy snapshot、materialization assumptions 和 lock-specific schema 全部留到 Phase 3。

---

## 17. Review Checklist

Phase 1 PR review 时应逐项确认：

### 17.1 Product / Architecture Alignment

- [ ] 是否保持 AAM 不是 Agent runtime？
- [ ] 是否保持 Manifest as source of truth？
- [ ] 是否保持 Registry as query projection？
- [ ] 是否保留 Agent-facing Asset Card boundary？
- [ ] 是否保留 trust / lifecycle / visibility / permissions？
- [ ] 是否保留 source provenance？
- [ ] 是否保留 graph-aware projection？
- [ ] 是否避免实现 Phase 2+ 范围？

### 17.2 Model Review

- [ ] Package / Asset / Profile 模型是否清晰？
- [ ] Manifest models 与 indexed models 是否分离？
- [ ] Asset Card projection 是否包含 Phase 1 硬字段？
- [ ] PermissionSpec 默认是否安全？
- [ ] TrustStatus 默认是否不自动 trusted？
- [ ] SourceProvenance 是否允许 future import workflow？

### 17.3 Validator Review

- [ ] 是否检测 duplicate ids？
- [ ] 是否检测 missing files？
- [ ] 是否检测 broken references？
- [ ] 是否检测 dependency cycles？
- [ ] 是否阻止 package root 外路径？
- [ ] 是否对 risky states 给出 warnings？

### 17.4 Registry Review

- [ ] Registry 是否包含 content hash？
- [ ] Registry 是否包含 Asset Card projection？
- [ ] Registry 是否包含 dependencies and reverse dependencies？
- [ ] Registry 是否支持基础 filters？
- [ ] Registry 是否不依赖 CLI？

### 17.5 CLI Review

- [ ] CLI 是否调用 service boundary？
- [ ] CLI 是否支持 JSON output？
- [ ] CLI error code 是否正确？
- [ ] CLI 是否不默认输出完整 asset content？

### 17.6 Test Review

- [ ] 是否有正常 fixture？
- [ ] 是否有错误 fixture？
- [ ] 是否覆盖 parser / validator / resolver / hash / registry / graph / CLI？
- [ ] Snapshot tests 是否稳定？

---

## 18. Phase 1 Completion Definition

Phase 1 可以视为完成，当且仅当：

1. 所有 Phase 1 work orders 已完成并合并。
2. 所有 acceptance criteria 通过。
3. CLI demo workflow 可以在本地执行。
4. Tests 全部通过。
5. Quickstart 已完成。
6. Example package 可用。
7. Phase 1 没有引入 Phase 2+ 的重型能力。
8. Phase 1 数据模型足以支撑 Phase 2 persistent registry 和 import service。

完成后建议打 tag：

```text
phase-1-core-package-system-mvp
```

或如果项目开始采用 semver：

```text
v0.1.0
```

---

## 19. Handoff to Phase 1.5

Phase 1 完成后，进入 Phase 1.5 Technical Spike Checkpoint。

Phase 1.5 需要基于 Phase 1 实际实现回答：

1. registry persistence 采用 SQLite、DuckDB 还是 JSON？
2. RegistryStore 如何映射当前 InMemoryRegistry？
3. UsageEvent / AuditLog / RejectionEvent 最小持久化形态是什么？
4. API framework 选择什么？
5. MCP framework 选择什么？
6. Profile closure / Assembly Plan / Package Lock 是否需要调整模型边界？
7. 前端技术栈选择什么？
8. graph visualization 技术栈选择什么？
9. CI / release / tag convention 是否稳定？

Phase 1 的产物必须让 Phase 1.5 能做技术选择，而不是重新定义核心资产模型。

---

## 20. Summary

Phase 1 的核心价值是建立 Agent Asset Management 的资产包底座。

它不追求完整产品体验，而追求以下稳定能力：

```text
package.yaml
  → typed models
  → parser
  → validator
  → content hash
  → Asset Card projection
  → in-memory registry
  → graph projection
  → CLI query/demo
```

如果 Phase 1 做得足够稳，Phase 2 的 persistent registry 和 import service、Phase 3 的 Profile / Assembly / Lockfile、Phase 4 的 Agent Gateway / MCP、Phase 5 的 materialization、Phase 6 的 Web Asset Browser 都可以自然接上。

如果 Phase 1 过窄，后续每个阶段都会补字段、补关系、补 policy、补 source、补 hash，最终导致架构返工。

因此 Phase 1 的原则是：

> 功能保持小，模型保持完整；实现保持简单，边界保持长期稳定。

