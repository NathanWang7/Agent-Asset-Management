# Agent Asset Management Foundation & Roadmap Spec

## 1. Status

Draft v0.4.1

本文档是 Agent Asset Management 项目的基石文档，不是第一阶段实现文档，也不是完整实现方案。

它回答七个问题：

1. **这个项目是什么？**
2. **这个项目不是什么？**
3. **它最终可以走到哪里？**
4. **为了到达最终形态，底层架构从第一天必须保留哪些能力？**
5. **外部 AI Agent 如何安全发现、评估、请求组装并使用资产？**
6. **Profile、Assembly Plan、Package Lock 与 Materialization 的关系是什么？**
7. **每个周级阶段应该交付什么，暂时不做什么？**

本文档不展开数据库表细节、前端组件细节、CLI 参数细节、具体 target adapter 渲染规则、MCP protocol 字段级实现或 GitHub importer 的字段级实现。

v0.4.1 在 v0.4 的基础上完成以下一致性修正，并保留 v0.4 的结构性升级：

- 将 Core MVP 与 MVP+ 分开，避免 Dashboard / Graph 与 Agent Gateway MVP 边界混乱。
- 将 minimal rejection-to-governance loop 前移到 Phase 6，完整治理编辑仍保留在 Phase 8。
- 为 UsageEvent / AuditLog 在 Phase 2 预留持久化占位，避免后续推荐反馈返工。
- 明确 Phase 1 的 Asset Card generation boundary，硬字段必须可投影，软字段可占位。
- 在 Phase 1.5 增加 Profile closure / Assembly / Lockfile 复杂度 probe。
- 统一 MCP tool 命名为 assembly-plan 语义，避免 package / bundle / lockfile 混淆。

v0.4 在 v0.3 的基础上完成以下结构性升级：

- 将项目定位从 `Agent Asset Workspace` 升级为 `Private Agent Asset Registry with Agent-facing Discovery and Assembly Layer`。
- 将 **External AI Agent** 纳入一等资产消费者。
- 新增 **Agent Gateway** 作为外部 Agent 与私有资产库之间的受控接口层。
- 明确 **MCP Server 是动态能力接口，Skill / AGENTS.md / Host Instruction Pack 是行为引导层**。
- 新增 **Agent-readable Asset Card**，作为外部 Agent 读取资产前的安全摘要投影。
- 新增 **Discovery Request / Assembly Plan / Package Lock / Materialization** 的核心模型。
- 明确 **Profile 是长期人工治理基线，Assembly Plan 是任务级动态组合建议**。
- 新增 Agent Gateway failure / degraded mode 原则：`Fail closed for asset access; fail soft for user task execution`。
- 将 Agent Gateway / MCP 能力从后期集成前移为核心路线图阶段。

---

## 2. One-sentence Definition

Agent Asset Management 是一个 **local-first、private-first、source-aware、graph-aware 的 Agent Asset Registry 与 Agent-facing Discovery and Assembly Layer**，用于结构化管理、导入、浏览、统计、关系建模、治理、发现、组装和导出个人或团队积累的 Agent 能力资产；它面向人类用户提供资产管理工作台，面向外部 AI Agent 提供受控的资产发现与组装接口，但不负责执行 Agent、不负责第三方依赖安装，也不提供公开资产市场。

简化表达：

```text
Human manages assets.
External Agent consumes assets.
AAM governs discovery, assembly, trust, dependency, rendering, and audit.
```

---

## 3. Target Users & Usage Scenarios

### 3.1 Target Users

本项目优先服务以下用户和消费者：

1. **Heavy AI Coding User / Human Asset Owner**  
   长期使用 Codex、Claude Code、Cursor、ChatGPT、OpenCode 等工具，积累了大量 prompts、rules、sub-agents、skills、MCP configs、workflow templates 和 host instructions。

2. **Personal Researcher / Builder**  
   在多个研究或开发项目之间复用 Agent 能力，但资产分散在不同仓库、配置文件、聊天记录和本地目录中。

3. **External AI Agent / Coding Agent**  
   代表 Claude Code、Codex、OpenCode、Cursor、Copilot、Gemini CLI 或其他 MCP-compatible clients。它不是资产所有者，也不是治理者，但它是资产消费者。它需要在执行任务前查询本地资产库，读取安全摘要，理解哪些能力可用，并请求 AAM 生成当前任务下合适的资产组合。

4. **Small Private Team**  
   希望在私有环境中共享、审查、复用和治理内部 Agent 资产，但不需要公开市场或复杂企业平台。

5. **Agent Capability Maintainer**  
   需要知道某个 prompt、skill、tool、workflow 或 MCP server 被哪些 profile / package / materialization 使用，修改后会影响什么。

### 3.2 Primary Usage Scenarios

典型使用场景：

1. **整理个人 Agent 资产库**  
   把散落在本地目录、GitHub 仓库和项目配置中的资产导入并结构化管理。

2. **构建场景化 Agent Profile**  
   例如 quant research、paper writing、backend development、code review、MCP-heavy project setup 等 profile。

3. **Agent-initiated Asset Discovery**  
   外部 AI Agent 接收到任务后，通过 AAM Agent Gateway 查询当前有哪些可用资产，读取 Asset Cards，并请求生成 task-specific Assembly Plan。

4. **基于 Profile 的动态组装**  
   外部 Agent 可以在已有 Profile 的基础上请求二次组装：保留 Profile 作为 baseline，并根据当前任务动态 add / remove / override assets。

5. **导出 / Materialize 给外部工具使用**  
   将某个 Profile 或 approved Assembly Plan 解析为 Package Lock，并 materialize 成 Codex、Claude Code、OpenCode、Cursor、ChatGPT 或 generic markdown/json 可消费的结构。

6. **浏览和统计资产**  
   通过 Web UI 查看所有 assets、packages、profiles、tags、targets、状态、trust、来源和健康度。

7. **理解资产关系**  
   通过关系图谱查看 package、asset、profile、assembly plan、lock、tag、target、source 之间的依赖、引用、组合和来源关系。

8. **治理资产质量与信任状态**  
   标记 trusted / unreviewed / sandbox_only / blocked，处理 stale assets、duplicate candidates、eval coverage、change impact 和 rejected recommendations。

---

## 4. Product Positioning & Boundaries

### 4.1 Positioning

本项目是一个 **local-first / private-first 的 Agent 资产注册表与组装控制平面**，用于统一管理个人或团队在 AI 开发过程中积累的各类 Agent 能力资产，并让外部 AI Agent 可以通过受控接口安全消费这些资产。

它不是简单的文件夹整理工具，也不是 pip/npm 风格包管理器，更不是公开资产市场。

它最终应该成为一个私有化的 **Agent Asset Registry + Agent Gateway**：

- 能结构化登记所有 Agent 资产；
- 能从本地目录和 GitHub 等来源导入资产；
- 能浏览任意资产的内容、元数据、版本、来源、依赖、trust 和使用情况；
- 能通过 Asset Card 向外部 Agent 提供安全、紧凑、可评估的资产摘要；
- 能统计资产规模、类型分布、质量状态、信任状态和复用情况；
- 能用关系图谱展示所有资产之间的依赖、引用、组合、来源和演化关系；
- 能让外部 Agent 请求发现、评估和组装当前任务所需的资产包；
- 能把 Profile 或 approved Assembly Plan 转换为可复现的 Package Lock；
- 能把 locked package materialize 给 Codex、Claude Code、OpenCode、ChatGPT、Cursor、MCP Host 等外部工具使用；
- 能帮助用户长期沉淀、治理和复用自己的 Agent 能力体系。

### 4.2 Non-Goals

即使最终版本也不应把项目边界无限扩大。

#### 4.2.1 不做 pip/npm 风格依赖安装器

系统可以记录 external dependencies，但不负责安装 Python、Node 或 system packages。

#### 4.2.2 不做公开资产市场

默认不提供公网发布、公开评分、公开搜索、用户体系和交易市场。

#### 4.2.3 不做通用 Agent Runtime

系统不直接执行 Agent，不替代 Codex、Claude Code、OpenCode、ChatGPT、Cursor、MCP Host 或用户自己的 runtime。

外部 Agent 执行任务；AAM 负责资产发现、组装、治理、锁定、渲染和审计。

#### 4.2.4 不默认暴露完整资产内容给外部 Agent

外部 Agent 默认只能读取 Inventory Metadata 与 Asset Card。完整内容读取、materialization 或写入行为必须受 visibility、trust、permission、policy 和用户确认约束。

#### 4.2.5 不允许外部 Agent 绕过治理策略

外部 Agent 不能因为 MCP 调用失败、资产缺失或用户拒绝，就绕过 trust、visibility、permission、dependency 或 materialization policy。

#### 4.2.6 不做重型企业权限系统作为早期目标

后续可以支持团队私有部署，但 MVP 不应被复杂权限模型拖垮。

#### 4.2.7 不做一开始就全自动理解所有资产

系统优先依赖 manifest 和显式元数据。语义相似度、自动标签、自动关系抽取可以后续增加，但不能替代显式事实来源。

---

## 5. Problems to Solve

随着 AI coding、agent workflow、MCP/plugin 生态的发展，用户会不断积累以下资产：

- system prompts
- sub-agents
- skills
- tools/plugins
- MCP server configs
- workflow templates
- project instructions
- reusable knowledge snippets
- evaluation cases
- environment/config examples
- host-specific instruction packs
- scripts and templates

如果这些资产只散落在不同项目、不同工具配置和不同聊天记录中，会产生几个问题：

1. **不可发现**：不知道自己已有多少资产，资产在哪里，适合什么场景。
2. **不可复用**：同一能力在不同项目中反复复制粘贴，容易漂移和失控。
3. **不可审计**：不知道某个 Agent 使用了哪些 prompt、tools、skills 和配置。
4. **不可版本化**：资产变化后，旧项目无法稳定复现原来的行为。
5. **不可组合**：难以把多个资产按清晰规则组合成一个可运行的 Agent profile 或 task package。
6. **不可导入**：已有本地资产和 GitHub 公共资产缺少统一进入系统的方式。
7. **不可浏览**：缺少统一前端查看资产内容和元数据。
8. **不可统计**：缺少资产规模、分布、健康度、信任状态和复用情况的全局视角。
9. **不可理解关系**：缺少图谱视角，无法理解资产之间的依赖、引用、来源和组合结构。
10. **外部 Agent 不知道本地有哪些能力**：Claude Code、Codex、OpenCode 等工具在执行任务时，无法动态查询用户已经沉淀的私有资产库。
11. **外部 Agent 难以评估资产是否适合当前任务**：缺少 agent-readable 的用途、权限、trust、context cost、quality、target compatibility 和 dependency closure 摘要。
12. **Profile 与 task-specific 组合容易分裂**：人类维护长期 profile，Agent 又需要动态组合当前任务资产，两者需要统一模型。
13. **拒绝推荐后没有治理闭环**：用户因为 trust warning 或推荐不合适而拒绝后，如果系统不记录和引导，资产会继续僵尸化或反复被推荐。
14. **Agent Gateway 失败时体验不确定**：MCP Server 未启动、超时或 policy block 时，外部 Agent 需要明确降级行为。

---

## 6. Final Product Vision

最终形态不应只是 CLI，而应包含以下能力层。

```text
External Agents / Hosts
  ├── Claude Code
  ├── Codex
  ├── OpenCode
  ├── Cursor / Copilot / Gemini CLI
  └── Generic MCP Clients

        │
        ▼

Agent Gateway
  ├── MCP Server
  ├── Local HTTP API
  ├── CLI fallback
  ├── Discovery API
  ├── Asset Card API
  ├── Assembly API
  ├── Trust / Permission Filter
  ├── Host Compatibility Filter
  ├── Context Budget Filter
  └── Degraded Mode Policy

        │
        ▼

Registry Core
  ├── Package Registry
  ├── Asset Registry
  ├── Profile Registry
  ├── Resource Registry
  ├── Dependency Graph
  ├── Trust / Lifecycle Metadata
  ├── Visibility Policy
  ├── Eval / Test Metadata
  └── Usage / Audit Metadata

        │
        ▼

Materialization Layer
  ├── Claude Code adapter
  ├── Codex adapter
  ├── OpenCode adapter
  ├── Cursor adapter
  ├── Generic Markdown adapter
  ├── Generic JSON adapter
  └── Future host adapters
```

### 6.1 Asset Repository Layer

管理资产源文件和 manifest。

负责：

- Package 管理；
- Asset 管理；
- Profile 管理；
- Asset Card metadata 管理；
- 版本信息；
- 文件路径与稳定身份映射；
- source provenance；
- 基础校验。

### 6.2 Import / Source Layer

负责把外部资产安全、可审计地带入系统。

负责：

- local directory import；
- local file import；
- GitHub public repository import；
- GitHub tag/release/commit pinning；
- source provenance；
- trust defaulting；
- import run report；
- imported package wrapper manifest。

### 6.3 Registry / Index Layer

从 manifest、资产文件和 source provenance 构建本地索引。

负责回答：

- 当前有哪些 packages？
- 有哪些 assets？
- 每个 asset 属于哪个 package？
- 每个 asset 来自哪里？
- 每个 asset 被哪些 profile 使用？
- 每个 asset 被哪些 assembly plan / package lock / materialization 使用？
- 每个 asset 有哪些依赖、引用和标签？
- 每个 asset 的 trust、status、visibility、permission risk 和 context cost 是什么？
- 哪些 assets 是孤立的、过期的、冲突的、高复用的或被反复拒绝的？

### 6.4 Agent Gateway Layer

这是 v0.4 新增的一等架构层。

Agent Gateway 是外部 AI Agent 与私有 AAM registry 之间的受控接口层。

负责：

- 让外部 Agent 查询可用资产；
- 让外部 Agent 读取安全的 Asset Card；
- 根据任务、目标宿主和约束生成候选资产；
- 请求 task-specific Assembly Plan；
- 解释 selected / excluded assets、风险、缺失依赖和 policy block；
- 根据 trust、visibility、permission、context budget 和 host compatibility 过滤资产；
- 在 MCP 不可用或调用失败时提供明确降级策略；
- 默认 read-only + propose-only；
- 不允许外部 Agent 绕过 registry 和 policy 直接读取或安装资产。

第一等接口应是 MCP Server；Local HTTP API 和 CLI 是次级接口，分别用于本地 UI、脚本、调试和非 MCP 客户端。

### 6.5 Host Instruction Pack Layer

Host Instruction Pack 不是资产库的事实来源，也不实现 registry 逻辑。

它的职责是告诉外部 Agent：

- 什么时候应该调用 AAM；
- 如何调用 AAM MCP tools；
- 如何解释 Assembly Plan；
- 如何处理 trust warning；
- 如何处理 gateway failure；
- 什么时候可以继续当前任务而不依赖 AAM。

典型交付物：

```text
Claude Code:
  AAM Skill + MCP config example

Codex:
  AGENTS.md + MCP config example

OpenCode:
  instructions/config pack

Generic MCP Client:
  README + server config template
```

原则：

> MCP 是动态能力接口；Skill / AGENTS.md / Host Instruction Pack 是行为引导层。

### 6.6 Asset Browser Layer

提供可视化浏览能力。

用户应该可以：

- 浏览所有 assets；
- 按 type、tag、package、target、status、visibility、source、trust 过滤；
- 查看单个 asset 的详情页；
- 查看 asset 内容预览；
- 查看 Agent-readable Asset Card；
- 查看 asset 的依赖、被依赖、被哪些 profile 使用；
- 查看 asset 的版本、hash、来源、更新时间和说明；
- 查看相关 assets；
- 查看该 asset 是否被外部 Agent 推荐、采纳或拒绝。

### 6.7 Statistics / Analytics Layer

提供资产统计与质量概览。

典型统计包括：

- asset 总数；
- package 总数；
- profile 总数；
- assembly plan 数量；
- package lock 数量；
- 按 asset type 分布；
- 按 target 分布；
- 按 tag 分布；
- 按 source 分布；
- 按 trust status 分布；
- internal/exported/shared 比例；
- orphan assets；
- broken references；
- dependency cycles；
- top reused assets；
- stale assets；
- repeatedly rejected assets；
- recently changed assets；
- profile 复杂度；
- package 健康度。

### 6.8 Relationship Graph Layer

这是项目最终最重要的差异化能力之一。

系统应该能够把所有资产呈现为类似知识图谱的关系图谱。

图谱中的节点可以包括：

- Package
- Asset
- Profile
- AssemblyPlan
- PackageLock
- MaterializationRun
- Export Target
- Tag
- Source
- ImportRun
- GitHubRepository
- LocalDirectory
- Tool / MCP Server
- Eval Case
- Version

图谱中的边可以包括：

- `package_contains_asset`
- `profile_includes_asset`
- `assembly_plan_selects_asset`
- `assembly_plan_excludes_asset`
- `assembly_plan_based_on_profile`
- `package_lock_locks_asset`
- `materialization_uses_lock`
- `asset_depends_on_asset`
- `asset_references_asset`
- `asset_uses_tool`
- `asset_targets_runtime`
- `asset_has_tag`
- `asset_imported_from_source`
- `package_imported_from_source`
- `asset_pinned_to_commit`
- `asset_replaced_by_asset`
- `asset_similar_to_asset`
- `eval_case_validates_asset`

其中有些边来自 manifest 的显式声明，有些边可以后续由系统分析生成。

MVP 不需要立刻实现完整图谱，但从第一天开始，数据模型必须是 graph-aware 的。

### 6.9 Composition / Assembly / Lock / Materialization Layer

负责把 Profile 或 Discovery Request 转换成可使用、可审计、可复现的资产组合。

职责：

- profile closure 计算；
- task-specific discovery；
- Assembly Plan 生成；
- dependency closure；
- conflict detection；
- trust / visibility / permission policy enforcement；
- Package Lock 生成；
- target-specific materialization；
- materialization diff；
- audit report。

目标工具可以包括：

- Codex
- Claude Code
- OpenCode
- ChatGPT
- Cursor
- MCP Host
- generic markdown
- generic JSON

导出不是简单复制文件，而是要基于依赖闭包生成稳定、可审计、可复现的产物。

### 6.10 Governance / Quality Layer

长期来看，系统不只是存资产，还应该帮助用户治理资产。

包括：

- lifecycle status：draft / active / deprecated / archived
- trust status：trusted / unreviewed / sandbox_only / blocked / needs_manual_review
- review notes
- rejection reason
- quality score
- test/eval coverage
- usage tracking
- agent recommendation tracking
- change impact analysis
- stale asset detection
- duplicate asset detection
- profile health check
- rejection-to-governance loop

---

## 7. Core Design Principles

### 7.1 Asset-first

系统的第一等公民是 Asset，而不是工具、项目或运行时。

### 7.2 Agent-consumable, not agent-owned

外部 AI Agent 是资产消费者，不是资产治理者。它可以请求发现、读取 Asset Card、解释 Assembly Plan，但不能默认绕过 AAM 的 policy 直接读取、安装、修改或删除资产。

### 7.3 Local-first / Private-first

默认工作模式是本地目录 + 本地索引 + 私有 Git 工作流。

后续可以扩展远程同步或私有服务器，但不能让核心能力依赖中心化服务。

### 7.4 Manifest-driven

每个资产包必须通过 manifest 显式声明资产身份、类型、路径、依赖、可见性、标签和 profile。

Manifest 是事实来源；Registry 是索引缓存和查询层。

### 7.5 Source-aware from day one

资产来源不是注释，而是资产可追溯性的一部分。

系统必须从早期就记录 source provenance，至少包括：

- source kind；
- original location；
- imported timestamp；
- content hash；
- resolved version anchor, if any。

### 7.6 Graph-aware from day one

即使第一阶段不做关系图谱 UI，也必须从第一天就显式记录关系。

至少要支持：

- package contains asset；
- profile includes asset；
- asset depends on asset；
- asset has tag；
- asset targets runtime；
- asset imported from source；
- asset trust status；
- profile / assembly / lock / materialization 的演进关系。

否则后续图谱会变成补丁工程。

### 7.7 Composable, not executable

系统负责描述、校验、索引、浏览、分析、发现、组装、锁定和导出资产组合；不直接承担 Agent 执行职责。

### 7.8 Profile as baseline, Assembly Plan as task-specific proposal

Profile 是长期、稳定、人工治理的场景化资产基线。

Assembly Plan 是动态的、任务特定的组合建议，可以从零生成，也可以基于已有 Profile 生成。

### 7.9 Package Lock as reproducibility boundary

Package Lock 是 approved Assembly Plan 或 Profile closure 经过解析后的可复现结果。它记录精确资产版本、content hash、依赖闭包、policy snapshot 和 target-host rendering assumptions。

### 7.10 MCP as capability interface, Skill as behavioral guide

MCP Server 提供动态查询和组装能力。Skill、AGENTS.md、instructions.md 等 host-specific instruction pack 只负责教外部 Agent 何时、为何、如何调用这些能力。

### 7.11 Fail closed for asset access, fail soft for user task execution

当 Agent Gateway 失败、超时或不可用时：

- 对资产访问必须保守处理，不能编造资产或绕过 policy；
- 对用户任务应尽量降级继续，使用当前项目上下文完成可完成的部分。

### 7.12 Stable identity over file paths

资产身份不能只依赖文件路径。

文件路径可以变化，但 asset id 应尽量稳定。

### 7.13 Content hash is required, but not necessarily identity

`content_hash` 必须存在，并用于：

- import provenance；
- registry index；
- package lock；
- materialization snapshot；
- stale/change detection；
- duplicate candidate detection。

但 `content_hash` 是否参与 Asset primary identity 仍然是后续设计问题。

默认判断：

```text
Stable logical identity: package_id:asset_id@package_version
Content hash: verification / change detection / snapshot integrity
```

### 7.14 Trust before automation

外部导入资产、自动推荐资产、Agent 组装资产都必须经过 trust / visibility / permission / policy 检查。

### 7.15 Small core, extensible types

核心系统只定义少量稳定概念；资产类型允许扩展。

---

## 8. Glossary

### Package

一组相关 Agent 资产的组织单元，通常对应一个本地目录和一个 `package.yaml`。

### Asset

可被 Agent 使用、组合、引用、评估或导出的最小语义单元，例如 prompt、agent、skill、tool、mcp_server、workflow、instruction、schema。

### Asset Card

面向外部 Agent 的安全、紧凑、可评估的资产摘要投影。

它不是完整 manifest，也不是完整内容。它用于让外部 Agent 在不读取完整资产内容的前提下判断资产是否适合当前任务。

### Profile

面向具体使用场景的长期资产组合基线，声明某个场景通常需要哪些 assets，以及默认面向哪个 target。

### Discovery Request

外部 Agent 或用户发起的资产发现请求，通常包含 task、target_host、base_profile、constraints、workspace hints 和 policy preferences。

### Assembly Plan

针对某个任务生成的资产组合建议。它可以从零生成，也可以基于已有 Profile 生成。它不是最终锁文件，也不必直接 materialize。

### Package Lock

经过解析和批准后的可复现资产组合快照，记录资产精确版本、content hash、依赖闭包、policy snapshot 和 target-host assumptions。

### Materialization

把 Package Lock 或 Profile closure 渲染成目标 host 可消费的文件、配置或目录结构的过程。

### Manifest

资产包的声明文件。它是 Package / Asset / Profile / dependency / metadata 的事实来源。

### Registry

由 manifest、资产文件、来源信息和 run records 构建的本地索引缓存，用于查询、统计、图谱、Agent Gateway 和 materialization。Registry 是可重建查询投影，不是唯一事实源。

### Resource

非 Agent 能力本身、但被资产引用或 materialization 使用的辅助资源，例如模板文件、schema、示例、fixture、静态说明、配置片段或图片。Resource 不应与 Asset 混淆；只有能被 Agent 直接使用、组合、评估或导出的语义单元才应建模为 Asset。

### Agent Gateway

外部 AI Agent 访问 AAM 私有资产库的受控接口层，通常通过 MCP Server 暴露动态能力。

### MCP Server

Agent Gateway 的第一等动态能力接口。它提供 list/search/card/propose_assembly_plan/validate_assembly_plan/explain_assembly_plan 等 tools。

### Host Instruction Pack

面向某个外部 Agent host 的行为引导包，例如 Claude Code Skill、Codex AGENTS.md、OpenCode instructions/config。它不实现 registry 逻辑，只指导 Agent 正确调用 AAM。

### Relationship Graph

从 registry 投影出的节点和边结构，用于展示 assets、packages、profiles、assembly plans、locks、tags、targets、sources 之间的关系。

### Source

资产来源，例如本地目录、本地文件、GitHub 仓库、GitHub release、手动创建等。

### SourceAdapter

负责从某类 source 中读取、解析、导入资产的适配器接口。

### ImportRun

一次导入 workflow 的记录，描述导入来源、导入结果、warnings、errors、trust defaults 和生成的 package/assets。

### Native Package

原生遵循本系统 `package.yaml` 规范的资产包。

### Imported Package

从外部来源导入后，由系统生成 wrapper manifest 管理的资产包。

### GraphProjection

从 registry 数据生成 graph nodes/edges 的过程或结果。

### Export Target / Target Host

资产组合要适配的外部工具或运行环境，例如 Codex、Claude Code、OpenCode、Cursor、ChatGPT、MCP Host。

### ExportPlan

导出前生成的计划，描述导出 profile 的 asset closure、目标结构、输出路径和潜在问题。

v0.4 后，长期应逐步用 Assembly Plan / Package Lock / MaterializationRun 替代过窄的 ExportPlan 概念。

### ExportRun / MaterializationRun

一次实际导出或 materialization workflow 的记录。

### Degraded Mode

当 Agent Gateway 不可用、超时、错误或被 policy 阻断时，外部 Agent 的降级行为模式。

### Work Order

阶段内部适合交给 Claude Code / Codex 实现的具体任务单元。

---

## 9. Core Concepts

### 9.1 Package

Package 是一组相关 Agent 资产的组织单元。

一个 package 通常对应一个本地目录，可以被 Git 管理。

Package 必须包含一个 manifest 文件。

```yaml
package:
  id: my-agent-assets
  name: My Agent Assets
  version: 0.1.0
  description: Personal reusable agent assets
```

Package 的职责：

- 声明自身身份和版本；
- 管理一组 assets；
- 声明 package-level metadata；
- 提供 profiles；
- 保留 source provenance；
- 成为 registry 和 graph 的顶层节点。

### 9.2 Asset

Asset 是可被 Agent 复用的最小语义单元。

常见 asset types：

- `prompt`
- `agent`
- `skill`
- `tool`
- `mcp_server`
- `workflow`
- `instruction`
- `knowledge`
- `eval_case`
- `template`
- `schema`
- `host_instruction_pack`

示例：

```yaml
assets:
  - id: code-reviewer
    type: agent
    path: agents/code_reviewer.md
    visibility: exported
    lifecycle_status: active
    trust_status: trusted
    description: Reviews code for correctness, maintainability, and risk.
    tags: [coding, review]
    target_hosts: [codex, claude_code]
    depends_on: []
```

Asset 的稳定身份建议为：

```text
package_id:asset_id@package_version
```

其中 `package_version` 用于复现，日常查询可以默认指向 latest/current。

### 9.3 Asset Card

Asset Card 是外部 Agent 的第一读取对象。

它回答：

- 这个 asset 是什么？
- 它适合什么任务？
- 它支持哪些 host？
- 它需要哪些权限？
- 它是否 trusted？
- 它大约消耗多少上下文？
- 它有哪些依赖？
- 它为什么可能被推荐或排除？

示例：

```yaml
asset_card:
  id: skill.polars-factor-debugger
  type: skill
  version: 0.3.0
  title: Polars Factor Debugger
  summary: Helps inspect Polars expressions, joins, window operations, and factor panel bugs.
  intended_use:
    - debug Polars factor computation
    - review lazy query logic
    - identify lookahead risk
  tags:
    - polars
    - factor-research
    - debugging
    - quant
  target_hosts:
    - claude_code
    - codex
    - opencode
  input_context:
    expects:
      - python code
      - polars dataframe schema
      - error traceback
  output_capabilities:
    - code review
    - bug diagnosis
    - safer rewrite suggestion
  dependencies:
    - prompt.polars-style-guide
    - schema.factor-panel-contract
  trust:
    status: trusted
    reviewed_by: local-user
  lifecycle:
    lifecycle_status: active
    maturity: stable
  safety:
    permissions:
      filesystem: read
      network: none
      shell: none
    risk_level: low
  quality:
    test_status: passing
    usage_count: 17
  context_cost:
    estimated_tokens: 1800
```

原则：

> 外部 Agent 应先读取 Asset Card，再决定是否请求 Assembly Plan。它不应默认直接读取完整 asset content。

### 9.4 Profile

Profile 是一个面向具体使用场景的长期资产组合基线。

例如：

- `quant-research-codex-profile`
- `paper-writing-chatgpt-profile`
- `backend-dev-claude-profile`
- `polars-debugging-opencode-profile`

Profile 不等于 Agent runtime。它只是声明某个场景通常需要哪些 assets，以及如何导出给目标工具。

```yaml
profiles:
  - id: quant-research
    target_host: codex
    description: Baseline profile for quant research coding tasks.
    includes:
      - agent:quant-researcher
      - skill:polars-performance
      - instruction:alpha-station-project-rules
```

Profile 是人工维护、长期存在的复用单元。

### 9.5 Discovery Request

Discovery Request 是外部 Agent 或用户请求 AAM 帮助发现资产的输入对象。

示例：

```json
{
  "task": "Review a Polars-based factor evaluation workflow and identify lookahead risks.",
  "target_host": "codex",
  "base_profile": "quant-research",
  "workspace": {
    "language": "python",
    "project_type": "quant-research",
    "paths": ["alphastation/library", "alphastation/experiment"]
  },
  "constraints": {
    "max_assets": 8,
    "max_context_tokens": 12000,
    "allow_unreviewed": false,
    "allow_network": false,
    "allow_shell": false
  }
}
```

### 9.6 Assembly Plan

Assembly Plan 是一个 task-specific package proposal。

它可以：

- 从零生成；
- 基于已有 Profile 生成；
- 动态添加任务相关资产；
- 动态排除不适合当前任务的 baseline asset；
- 标记 override；
- 解释 selected / excluded assets；
- 展示风险、缺失依赖和 policy block。

示例：

```yaml
assembly_plan:
  task: review AlphaStation library workflow
  target_host: codex
  base_profile: quant-research
  selected_assets:
    - skill.polars-factor-debugger@0.3.0
    - prompt.lookahead-risk-review@0.2.0
    - schema.factor-panel-contract@0.1.0
  profile_delta:
    added:
      - prompt.lookahead-risk-review@0.2.0
    removed: []
    overridden: []
  excluded_assets:
    - mcp.remote-market-data:
        reason: requires network permission
  rationale:
    - Polars debugging is relevant to the current codebase.
    - Lookahead review is relevant to label and tradability logic.
    - Factor panel schema helps validate datetime/asset/value contracts.
  risks:
    - Some assets require broad codebase context.
  missing:
    - No dedicated OpenCode adapter test found.
```

Assembly Plan 不是 Package Lock，不保证可复现。它是可解释、可审查、可拒绝、可修正的计划。

### 9.7 Package Lock

Package Lock 是 approved Assembly Plan 或 Profile closure 经过解析后的可复现结果。

它应该记录：

- target host；
- selected assets；
- exact versions；
- content hashes；
- dependency graph；
- policy snapshot；
- trust snapshot；
- source provenance；
- materialization assumptions。

示例：

```yaml
package_lock:
  target_host: codex
  created_for_task: review AlphaStation library workflow
  base_profile: quant-research
  assets:
    - id: skill.polars-factor-debugger
      version: 0.3.0
      content_hash: sha256:...
    - id: prompt.lookahead-risk-review
      version: 0.2.0
      content_hash: sha256:...
  dependency_graph:
    nodes: []
    edges: []
  policy_snapshot:
    allow_unreviewed: false
    allow_network: false
    allow_shell: false
```

### 9.8 Profile / Assembly / Lock / Materialization Relationship

AAM 支持两种互补的组合路径。

#### Path A: Human-driven Profile Composition

```text
Human creates/refines Profile
  → AAM resolves Profile closure
  → Package Lock
  → Materialization
```

#### Path B: Agent-driven Dynamic Assembly

```text
External Agent receives task
  → Discovery Request
  → Asset Card inspection
  → Assembly Plan
  → User or policy approval
  → Package Lock
  → Materialization
```

#### Path C: Profile-based Dynamic Assembly

```text
External Agent receives task
  → Discovery Request with base_profile
  → AAM treats Profile as baseline
  → AAM adds/removes/overrides task-specific assets
  → Assembly Plan with profile_delta
  → Approval
  → Package Lock
  → Materialization
```

产品语义：

- Profile answers: **What do I usually use for this scenario?**
- Assembly Plan answers: **What should this agent use for this task right now?**
- Package Lock answers: **What exact assets were approved and resolved?**
- Materialization answers: **What files/configs should be written for the target host?**

### 9.9 Registry

Registry 是本地索引，用于服务查询、前端、统计、图谱、Agent Gateway 和 materialization。

Registry 不应成为唯一事实来源。

```text
Manifest + Asset files + Source provenance
  -> Indexer
  -> Registry
  -> CLI / API / UI / Graph / Agent Gateway / Materialization
```

### 9.10 Relationship Graph

Relationship Graph 是从 registry 中投影出来的图结构。

它不是另一份人工维护的数据，而是由 manifest、registry、导入来源、内容分析、usage/audit 记录共同生成。

早期图谱以显式关系为主；后期可以加入自动推断关系。

### 9.11 Export Target / Target Host

Export Target 表示资产组合要适配的外部工具或运行环境。

常见 target：

- `codex`
- `claude_code`
- `opencode`
- `chatgpt`
- `cursor`
- `mcp_host`
- `generic_markdown`
- `generic_json`

---

## 10. Agent Access Levels and Visibility

外部 Agent 不应获得无限制资产访问权。

AAM 应通过分层访问模型暴露信息。

### 10.1 Level 1 — Inventory Metadata

外部 Agent 可以看到：

```text
asset id
type
title / description summary
tags
version
lifecycle status
target host compatibility
basic trust status
```

适合：`list_assets` / `search_assets`。

### 10.2 Level 2 — Asset Card

外部 Agent 可以看到：

```text
intended use
input expectations
output capabilities
dependencies
trust status
permission risk
quality status
estimated context cost
host compatibility
```

适合：`get_asset_card`。

### 10.3 Level 3 — Content Preview

外部 Agent 可以看到安全预览：

```text
prompt 摘要
skill 使用说明摘要
workflow 步骤摘要
schema 摘要
profile 摘要
```

但不应直接暴露 secret、敏感路径、完整脚本或高风险配置。

### 10.4 Level 4 — Full Content / Materialization

完整内容读取或 materialization 必须受 policy 控制：

- `trusted` 资产可以按 policy 完整读取或 materialize；
- `unreviewed` 资产默认只能 preview 或作为带 warning 的候选；
- `sandbox_only` 资产不能进入默认 materialization；
- `blocked` 资产不可用，默认不可推荐；
- 需要 shell / network / filesystem broad access 的资产必须显式 warning；
- materialization 默认需要用户确认或明确 policy 允许。

### 10.5 Visibility Semantics

`visibility` 控制资产能否离开当前 package 或被外部 Agent 消费，但它不替代 trust、permission、target compatibility 或 access level policy。

```text
internal:
  只能在当前 package 内部使用。不允许外部 Agent 完整读取，不允许跨 package 直接依赖，不进入默认 materialization。

exported:
  可以进入 Profile、Assembly Plan、Package Lock 和 materialization，但仍需通过 trust、permission、target_host 与 policy gate。

shared:
  可以被其他 package、workspace-level Profile 或 Assembly Plan 引用。shared 不等于 public；它仍然受 trust、permission、visibility 和 workspace boundary 控制。
```

如果 Phase 1 不实现跨 package 依赖，`shared` 可以先被解析和校验但不开放跨包 materialization。

---

## 11. Agent Gateway

### 11.1 Responsibility

Agent Gateway 是受控接口层，不是 Agent runtime。

它负责：

- 发现资产；
- 投影 Asset Card；
- 生成候选资产；
- 计算 relevance / trust / compatibility / risk / cost；
- 生成 Assembly Plan；
- 验证 Assembly Plan；
- 解释选择和排除理由；
- 触发 lock / materialization 前的 policy gate；
- 记录 audit / usage / rejection 信号。

### 11.2 Primary Interface: MCP Server

第一版 MCP Server 建议提供以下 tools：

```text
list_assets
search_assets
get_asset_card
get_asset_dependencies
propose_assembly_plan
explain_assembly_plan
validate_assembly_plan
```

后续可增加但默认禁用或 gated：

```text
read_asset_full_content
create_package_lock
materialize_package
record_rejection
record_feedback
```

### 11.3 CLI and Local HTTP API

CLI 和 Local HTTP API 仍然重要，但不是外部 Agent 的第一等动态协议。

建议角色：

```text
CLI:
  human workflow, scripting, debugging, CI smoke tests

Local HTTP API:
  Web UI backend, local automation, non-MCP clients

MCP Server:
  external agent dynamic discovery and assembly
```

### 11.4 Discovery and Assembly Scoring

早期不需要复杂 embedding search。

MVP 可以基于显式 metadata 和规则评分：

```text
score =
  tag_match_score
+ type_match_score
+ target_host_compatibility_score
+ lifecycle_score
+ trust_score
+ dependency_completeness_score
+ quality_score
- permission_risk_penalty
- context_cost_penalty
- missing_dependency_penalty
- repeated_rejection_penalty
```

后期可以加入：

- full-text search；
- semantic search；
- similar asset detection；
- task-to-asset embedding relevance；
- usage feedback learning。

### 11.5 Gateway Failure and Degraded Mode

外部 Agent 应把 AAM 视为受控能力提供者，而不是完成用户任务的唯一前提。

当 AAM MCP Server 未启动、无法连接、响应超时、workspace 未初始化、search 返回空、policy 阻断或某个 tool 调用失败时，外部 Agent 不应：

- 无限重试；
- 编造资产；
- 声称隐藏资产存在；
- 绕过 trust、visibility、permission 或 materialization policy；
- 因 AAM 不可用而完全阻塞一个原本可以继续推进的用户任务。

推荐原则：

> Fail closed for asset access. Fail soft for user task execution.

降级策略：

| Failure Case | Expected Agent Behavior |
|---|---|
| MCP Server unavailable | 说明 AAM discovery 不可用，继续使用当前项目上下文。 |
| Tool timeout | 最多重试一次，然后降级。 |
| Workspace not initialized | 提示用户初始化或连接 workspace；若非必要则继续任务。 |
| Search returns empty | 说明没有找到匹配资产，不要虚构资产。 |
| Policy block | 解释 block 原因，不使用该资产。 |
| Asset Card read failure | 排除该资产或标记为 unavailable。 |
| Materialization denied | 不写入文件，改为解释 plan 和所需确认。 |

Host Instruction Pack 必须包含这些行为要求。


### 11.7 Gateway Security and Workspace Boundary

Agent Gateway 默认是本地、私有、workspace-scoped 的接口，而不是公开服务。

MVP 级别至少应遵守：

- 默认通过 stdio 或 localhost 暴露，不默认监听公网地址；
- 每个请求应携带或推断 `target_host` / `client_name`；
- Gateway 只能访问当前绑定 workspace 的 registry；
- 不同 workspace 之间不能默认互相读取资产；
- full content read、lock、materialization 和所有写操作必须经过 policy gate；
- audit log 应记录 client、tool、request、selected assets、policy decision、error/degraded-mode result；
- Gateway failure 不能成为绕过 trust、visibility、permission 或 materialization policy 的理由。

复杂认证、团队 RBAC 和远程 server mode 可以后置，但本地 workspace boundary 必须从第一版 contract 中保留。

---

## 12. Asset Source & Import Model

资产不一定一开始就诞生在本系统内部。

系统必须支持从不同来源导入资产，并保留来源信息、版本信息和可追溯性。

因此，本项目从早期开始就应该区分两个概念：

```text
Asset Source = 资产从哪里来
Asset Package = 系统如何管理它
```

不要把“本地文件夹”“GitHub 仓库”“系统内部 package”混为一谈。

### 12.1 Source Kinds

系统应逐步支持以下 source kinds：

```text
local_directory
local_file
github_repository
github_release
github_path
manual_created
```

MVP 不需要支持所有 source kinds，但数据模型应允许扩展。

### 12.2 Local Import Modes

本地资产导入通常没有天然版本管理，因此不能假设它有语义版本。

本地导入应支持三类模式：

1. **Adopt Mode**  
   直接把已有本地目录登记为 package，不复制文件。适合已有目录结构且希望轻量接管的场景。

2. **Copy / Snapshot Mode**  
   把本地资产复制到 managed package 目录中。适合需要可复现导出和稳定快照的场景。

3. **Reference Mode**  
   只记录外部路径引用，不接管文件。适合临时资产或大型外部目录，但可复现性最弱。

早期优先级：

```text
Phase 1: only source provenance fields
Phase 2: local adopt import + local copy/snapshot import
Later: reference mode if needed
```

### 12.3 GitHub Import Rules

GitHub 导入与本地导入不同，因为 GitHub 仓库天然具有版本坐标。

关键规则：

1. 用户可以输入 branch、tag、release 或 commit。
2. 系统导入时必须解析为具体 commit SHA。
3. 可复现性以 `resolved_commit` 为准，而不是 branch name。
4. 如果导入自 tag/release，应同时记录 tag/release 名称和 commit SHA。
5. 如果导入自 branch，应把 branch 当作更新通道，而不是稳定版本。
6. 后续更新必须通过 explicit upgrade/import run 完成，不能静默漂移。
7. 外部导入资产默认不应是 `trusted`。

GitHub 资产版本优先级：

```text
tag / release version > commit SHA > branch snapshot
```

但无论如何，实际复现都应 pin 到 commit SHA。

### 12.4 Native Package vs Imported Package

导入后的资产可以有两种管理形态。

#### Native Package

资产原生遵循本系统的 `package.yaml` 规范。

这种情况下系统可以直接 index、validate、query 和 materialize。

#### Imported Package

资产来源并不遵循本系统规范，需要系统生成 wrapper manifest。

```text
external source
  ↓
source adapter
  ↓
generated package.yaml
  ↓
managed imported package
```

Imported Package 必须保留 source provenance，不能伪装成原生资产。

### 12.5 ImportRun

导入本身应该是可审计的 workflow。

ImportRun 的价值：

- 追踪某批资产从哪里来；
- 支持导入失败回滚；
- 支持后续 upgrade diff；
- 支持 UI 展示资产来源；
- 支持图谱中的 imported-from 关系；
- 支持 trust defaulting 和 review workflow。

字段级设计进入后续 Import System Spec，不在本基石文档中展开。

### 12.6 Import-related Graph Relations

为了支持未来图谱，导入来源也应该成为图谱的一部分。

新增节点类型：

- Source
- ImportRun
- GitHubRepository
- LocalDirectory

新增边类型：

- `asset_imported_from_source`
- `package_imported_from_source`
- `import_run_created_asset`
- `import_run_created_package`
- `asset_pinned_to_commit`
- `asset_tracks_branch`

这样用户不仅能看到资产之间的关系，也能看到资产来源和版本锚点。

---

## 13. Development Workflow & GitHub Coupling

项目开发可以强依赖 GitHub workflow，但产品核心不应该强耦合 GitHub。

这两个问题必须分开：

```text
Development process: 可以强耦合 GitHub
Product architecture: 不应强耦合 GitHub
```

### 13.1 Recommended Development Workflow

开发过程建议采用 GitHub + PR 驱动。

原因：

- 每个阶段可以对应 milestone；
- 每个 work order 可以对应 issue；
- 每个实现任务可以通过 PR 合入；
- AI coding 工具非常适合在分支上完成局部任务；
- PR diff 便于人类 review；
- CI 可以保障测试和格式化；
- GitHub history 可以自然形成设计和实现审计记录。

推荐结构：

```text
Milestone = Phase
Issue = Work Order
Branch = Implementation attempt
Pull Request = Reviewable change set
CI = Automated acceptance gate
Release/Tag = Stable phase snapshot
```

### 13.2 PR-based AI Coding Loop

建议每个 work order 采用以下循环：

```text
1. Write/confirm work order spec
2. Create branch
3. Let Claude Code / Codex implement
4. Run tests locally
5. Open PR
6. Review diff
7. Ask AI to fix review comments
8. Run CI
9. Merge
10. Update phase progress
```

PR 不只是代码合并工具，也是 AI coding 的质量控制边界。

### 13.3 GitHub as Development Control Plane

开发期可以充分利用 GitHub：

- Issues 管理 work orders；
- Milestones 管理 phases；
- Pull Requests 管理代码变更；
- GitHub Actions 跑测试；
- Releases/Tags 标记阶段完成；
- Discussions 或 PR comments 记录设计争议；
- Projects 看板管理阶段进度。

这属于开发治理，不等于产品运行时依赖 GitHub。

### 13.4 Product Should Use SourceAdapter, Not GitHub-hardcoding

虽然开发过程可以强依赖 GitHub，但产品内部应通过 SourceAdapter 抽象支持不同来源。

```text
SourceAdapter
  ├── LocalDirectorySourceAdapter
  ├── GitHubSourceAdapter
  ├── GitSourceAdapter
  └── Future adapters...
```

产品核心只依赖 SourceAdapter interface，不直接到处写 GitHub 逻辑。

这样未来可以扩展：

- GitLab；
- Gitee；
- private Git server；
- local bare repo；
- zip archive；
- object storage。

### 13.5 GitHub Coupling Decision

最终决策：

1. **开发流程强耦合 GitHub：推荐。**  
   使用 GitHub Issues / PR / Actions / Releases 推进开发。

2. **产品导入能力优先支持 GitHub：推荐。**  
   因为 GitHub 是 Agent 资产最常见的公共来源之一。

3. **产品核心架构强耦合 GitHub：不推荐。**  
   应通过 SourceAdapter 和 provenance model 抽象来源。

4. **阶段交付与 GitHub tag/release 绑定：推荐。**  
   每个 phase 完成后可以打 tag，例如 `phase-1-core-package-mvp` 或 `v0.1.0`。

---

## 14. Minimal Manifest Model

为了支持未来前端、统计、导入、图谱、Agent Gateway 和 materialization，MVP 的 manifest 不能过窄。

建议第一阶段保留以下字段：

```yaml
package:
  id: string
  name: string
  version: string
  description: string
  tags: []
  source:
    kind: manual_created | local_directory | github_repository
    original_location: string | null
    resolved_ref: string | null

assets:
  - id: string
    type: string
    path: string
    visibility: internal | exported | shared
    lifecycle_status: draft | active | deprecated | archived
    trust_status: trusted | unreviewed | sandbox_only | blocked | needs_manual_review
    description: string
    tags: []
    depends_on: []
    target_hosts: []
    permissions:
      filesystem: none | read | write | broad
      network: none | read | broad
      shell: none | limited | broad
    context_cost:
      estimated_tokens: int | null
    agent_card:
      title: string | null
      summary: string | null
      intended_use: []
      input_context: {}
      output_capabilities: []
      risk_level: low | medium | high | unknown
    metadata: {}

profiles:
  - id: string
    target_host: string
    description: string
    includes: []
    tags: []
```

### 14.1 Required Rules

1. `package.id` 在本地 registry 中必须唯一。
2. 同一个 package 内，`asset.id` 必须唯一。
3. `asset.path` 必须存在，除非该 asset type 明确允许 virtual / generated content。
4. `profile.includes` 引用的 asset 必须存在。
5. `depends_on` 引用的 asset 必须存在。
6. `visibility=internal` 的 asset 不允许被其他 package 直接引用，也不允许外部 Agent 完整读取。
7. `lifecycle_status=archived` 的 asset 默认不参与新 profile、assembly plan 或 materialization。
8. `trust_status=blocked` 的 asset 默认不可推荐、不可组装、不可 materialize。
9. `trust_status=unreviewed` 的 asset 如果进入 Assembly Plan，必须带 warning。
10. materialize Profile closure、approved Assembly Plan 或 Package Lock 时，只输出闭包内需要的 assets。
11. 依赖关系必须进入 registry，不能只在导出时临时计算。
12. source provenance 必须进入 registry，不能只保存在 import log。
13. 所有可视化图谱需要的基础关系必须能从 registry 中恢复。
14. `content_hash` 必须由 indexer 计算并进入 registry；是否写回 manifest 由后续实现决定。
15. Asset Card 可以由 manifest 显式提供，也可以由 indexer 从 manifest 和内容摘要生成，但不能伪造 trust 或 permission 信息。
16. Phase 1 至少必须生成 Asset Card projection 的硬字段：id、type、version、title/summary fallback、tags、target_hosts、dependencies、trust_status、lifecycle_status、permissions、risk_level、estimated_context_cost。
17. intended_use、input_context、output_capabilities 等软字段可以先为空或来自 manifest，不要求 Phase 1 自动语义生成。
18. 自动生成 Asset Card 时必须执行 redaction，不得暴露 secret、token、API key、cookie、私密绝对路径或完整高风险脚本内容。

### 14.2 Manifest Splitting Policy

MVP 阶段允许 profiles 与 assets 位于同一个 manifest。

如果未来出现以下情况，再设计 manifest splitting：

- profile 数量显著膨胀；
- profile 需要跨 package 组合；
- Assembly Plan 或 Package Lock 需要独立文件生命周期；
- 单个 manifest 难以 review；
- UI 编辑 manifest 时冲突频繁。

默认策略：先简单，后拆分；不要在 Phase 1 为不存在的规模问题引入复杂结构。

### 14.3 Lockfile Boundary

Package Lock 不应与 package manifest 混在一起。

Package 是源码/资产组织单元；Package Lock 是某次 Profile closure 或 approved Assembly Plan 的可复现使用快照。二者名称相近，但生命周期、用途和事实来源不同。

推荐方向：

```text
package.yaml          # stable source-of-truth declarations
package.lock.yaml     # resolved reproducibility snapshot
assembly_runs/*.json  # task-specific proposal records
materialization_runs/*.json  # host rendering records
```

字段级设计进入 Phase 3 / Phase 4A implementation spec。

---

## 15. Weekly Milestone Roadmap for AI-assisted Development

本项目的阶段划分不应该等同于一次 Claude Code / Codex 对话的任务粒度。

更合理的定义是：

> 一个阶段是一个周级别的工程里程碑，通常需要经历 spec → plan → execute → debug → review → polish 多轮迭代，并最终产出一个可运行、可测试、可演示的系统切片。

Claude Code / Codex 的使用方式应该是：

- **阶段级别**：由人类确定目标、边界、验收标准和架构约束；
- **任务级别**：交给 AI coding 工具实现具体模块、测试、修复、重构和文档；
- **评审级别**：由人类和 AI 共同审查设计一致性、代码质量和长期可维护性。

### 15.1 Phase Design Criteria

一个合格的阶段应该满足：

1. **时间尺度**：通常是 3-7 天的集中开发，而不是一两次对话。
2. **复杂度**：包含多个可拆分 work orders，但不至于跨越太多系统边界。
3. **产物明确**：阶段结束后必须有可运行、可测试、可演示的结果。
4. **可验收**：有明确 acceptance criteria、fixtures、tests 或 demo workflow。
5. **可回滚**：阶段失败时，不应污染前一阶段的稳定成果。
6. **架构递进**：每个阶段都应该为下一阶段提供稳定接口，而不是临时实现。
7. **认知负载可控**：一个阶段最多引入 1-2 个主要新系统边界。

阶段内部可以拆成多个 AI coding work orders，例如：

```text
Phase Spec
  → Implementation Plan
  → Work Order 1: models
  → Work Order 2: parser / validator
  → Work Order 3: tests / fixtures
  → Work Order 4: CLI or API integration
  → Debug Pass
  → Review Pass
  → Polish / Docs
```

---

### 15.2 Phase 0 — Foundation & Architecture Lock

建议周期：0.5-1 周

目标：锁定项目长期方向、核心概念、边界和第一批工程决策。

交付物：

- Foundation & Roadmap Spec；
- Product Brief；
- Glossary；
- non-goals；
- package / asset / profile / asset_card / assembly_plan / package_lock / registry / graph / source 的概念边界；
- Agent Gateway / MCP / Host Instruction Pack 的架构定位；
- 第一阶段 implementation spec；
- 初始技术栈选择。

完成标准：

- 能明确判断后续任何功能是否属于项目边界；
- 能开始编码 Phase 1；
- 不再反复重写项目定位；
- Profile、Assembly Plan、Package Lock、Materialization 的关系已明确。

---

### 15.3 Phase 1 — Core Package System MVP

建议周期：1 周

目标：完成本项目的最小资产描述、校验和本地索引闭环。

这是项目真正的底座阶段，不只是 schema，也不只是 CLI。阶段结束时，系统应该已经能管理一个最小资产包，并为未来 Agent Gateway 保留 Asset Card / trust / permission / target compatibility 字段。

核心能力：

- package directory 规范；
- `package.yaml` manifest schema；
- Package / Asset / Profile typed models；
- Asset Card minimal model；
- Trust status minimal model；
- Permission metadata minimal model；
- basic source provenance model；
- manifest parser；
- validator；
- reference resolver；
- dependency cycle check；
- content hash；
- in-memory registry；
- graph-aware nodes/edges projection；
- example packages and fixtures；
- 最小 CLI：`init / validate / index / list / show`。

交付物：

- core domain models；
- manifest parser；
- validator；
- index builder；
- graph projection；
- fixture packages；
- CLI MVP；
- unit tests；
- quickstart doc。

本阶段不做：

- 不做完整 GitHub importer；
- 不做复杂 ImportRun 持久化；
- 不做持久化 registry DB；
- 不做 HTTP API；
- 不做 MCP Server；
- 不做 Web UI；
- 不做 target-specific materialization；
- 不做复杂治理流程。

完成标准：

- 用户可以初始化一个 package；
- 用户可以登记 prompt / agent / skill / mcp_server 等资产；
- 系统可以校验 manifest 和文件结构；
- 系统可以构建本地 in-memory registry；
- 系统可以列出和查看 asset；
- 系统可以输出 graph nodes/edges JSON；
- registry 中包含 content hash、source provenance、trust status 和 Asset Card projection 所需字段；
- 核心错误场景有测试覆盖。

---

### 15.4 Phase 1.5 — Technical Spike Checkpoint

建议周期：0.5 周

目标：在进入持久化、API、MCP 和前端之前，对关键技术栈做轻量验证，避免后续阶段接口重工。

需要验证的问题：

- registry storage：SQLite / DuckDB / JSON；
- UsageEvent / AuditLog 最小持久化形态；
- API framework：FastAPI / Litestar / other；
- MCP framework / SDK；
- Profile closure、Assembly Plan、profile_delta、Package Lock 的算法复杂度和接口边界；
- Phase 3 是否只实现最小 explain/validate，是否将更完整的 explain/validate API 拆入 Phase 4A；
- frontend stack：React + Vite / Next.js / other；
- graph visualization：React Flow / Cytoscape.js / Sigma.js / G6；
- package layout and build tooling；
- CI workflow；
- GitHub PR template and issue template。

交付物：

- Technical Spike Note；
- registry storage decision；
- UsageEvent / AuditLog placeholder decision；
- Profile closure / Assembly / Lockfile complexity note；
- API/MCP/frontend/graph UI 初步选择；
- CI baseline；
- phase release/tag convention。

完成标准：

- Phase 2 不再纠结 registry storage；
- Phase 4A/4B 不再临时选择 API/MCP 技术栈；
- Phase 6 不再临时选择 frontend 技术栈；
- Phase 7 不再临时选择 graph visualization library。

---

### 15.5 Phase 2 — Persistent Registry, Import Service & CLI Usability

建议周期：1-2 周

目标：把 Phase 1 的内存能力升级为可复用的本地 registry 服务，并实现资产进入系统的正式导入入口。

这一阶段解决两个核心问题：

1. 系统如何持久化和查询已经登记的资产？
2. 用户如何把已有本地资产或 GitHub 公共资产导入系统？

核心能力：

- registry persistence；
- registry rebuild；
- RegistryStore；
- RegistryService；
- AssetQueryService；
- GraphQueryService；
- StatsService；
- reverse dependency query；
- orphan asset detection；
- broken reference summary；
- SourceAdapter interface；
- LocalDirectorySourceAdapter；
- local adopt import；
- local copy/snapshot import；
- GitHubSourceAdapter v0；
- GitHub public repo import；
- GitHub ref resolution to commit SHA；
- ImportRun report；
- UsageEvent / AuditLog placeholder store；
- rejection event minimal schema；
- trust defaulting for imported assets；
- CLI 输出体验增强；
- JSON output mode。

交付物：

- local registry storage；
- stable query services；
- source provenance model；
- import service；
- local import workflow；
- GitHub public import workflow；
- ImportRun report；
- UsageEvent / AuditLog minimal models；
- stats model；
- enhanced CLI：`import / stats / graph export`；
- query tests；
- import tests；
- CLI smoke tests；
- registry rebuild workflow。

本阶段不做：

- 不做 Web UI；
- 不做 HTTP API，除非作为极轻预研；
- 不做 MCP Server；
- 不做复杂 graph layout；
- 不做 profile materialization system；
- 不做 GitHub private repo auth；
- 不做自动追踪 GitHub branch 更新；
- 不做复杂 upstream merge。

完成标准：

- 系统不需要每次查询都重新扫描文件；
- CLI、未来 API、未来 UI、未来 MCP Server 可以复用同一服务层；
- 用户可以查看资产统计、上下游依赖和 graph JSON；
- registry 可删除重建，结果确定性一致；
- 用户可以从本地目录导入资产；
- 用户可以从 GitHub public repo/tag/commit 导入资产；
- GitHub 导入结果 pin 到 resolved commit SHA；
- 导入资产默认进入 unreviewed 或 needs_manual_review 状态；
- 导入过程产生 ImportRun report，并可在失败时安全退出；
- registry persistence 为 UsageEvent / AuditLog / RejectionEvent 预留最小表或集合，早期可以只写入有限事件，不实现复杂推荐学习。

---

### 15.6 Phase 3 — Profile Composition, Assembly Plan & Lockfile

建议周期：1-2 周

复杂度提示：本阶段同时涉及 Profile closure、Assembly Plan、profile_delta 和 Package Lock，必须控制切片。Phase 3 应优先完成可测试的最小闭环；详细 explain/validate API 可以在 Phase 4A 扩展。

目标：让系统从“能管理资产”进入“能组合、计划和锁定资产”。

这是第一个真正体现实用价值的阶段：用户可以定义 profile，系统可以计算 profile closure，也可以根据任务生成 Assembly Plan，并把批准后的组合解析为 Package Lock。

核心能力：

- profile includes 解析；
- dependency closure；
- Profile closure model；
- DiscoveryRequest model；
- AssemblyPlan model；
- profile_delta model；
- basic rule-based asset recommendation；
- trust / permission / target compatibility filtering；
- AssemblyPlan minimal validation；
- PackageLock model；
- lockfile generation；
- dry-run；
- generic markdown materialization preview；
- generic JSON materialization preview；
- materialization snapshot model；
- diff between previous lock/materialization and current plan。

交付物：

- composition model；
- assembly planner；
- lockfile model；
- generic materialization preview；
- CLI：`profile closure / discover / assemble / lock / materialize --dry-run`；
- fixtures；
- snapshot tests。

本阶段不做：

- 不做 MCP Server；
- 不做 Web UI；
- 不做所有 target adapters；
- 不调用外部工具 API；
- 不执行 Agent；
- 不做 secret 注入。

完成标准：

- 给定一个 profile，系统能计算完整 asset closure；
- 给定一个 task + target_host，系统能生成基础 Assembly Plan；
- 给定 task + base_profile，系统能生成带 profile_delta 的 Assembly Plan；
- Assembly Plan 能以 reason codes / warnings 的形式解释 selected / excluded assets、风险和缺失依赖；
- approved Assembly Plan 能生成 Package Lock；
- Package Lock 记录 content hash 和 policy snapshot；
- 用户可以 dry-run 查看 materialization preview；
- 输出结果可复现、可审计、可 diff。

---

### 15.7 Phase 4A — Local Agent Gateway API

建议周期：0.5-1 周

目标：把 Phase 2/3 的服务层包装成稳定的本地 Agent Gateway API，为 MCP Server、Web UI 和本地自动化做准备。

这不是普通 HTTP API 阶段，而是 Agent-facing query and assembly contract 阶段。

核心能力：

- local API server；
- OpenAPI schema；
- asset endpoints；
- asset card endpoints；
- profile endpoints；
- discovery endpoint；
- assembly endpoint；
- package lock endpoint；
- stats endpoint；
- graph endpoint；
- materialization preview endpoint；
- API response models；
- gateway error model；
- degraded-mode response semantics；
- API smoke tests。

建议端点形态：

```text
GET  /v1/assets
GET  /v1/assets/{asset_id}
GET  /v1/assets/{asset_id}/card
GET  /v1/assets/{asset_id}/dependencies
GET  /v1/profiles/{profile_id}/closure
POST /v1/discover
POST /v1/assemble
POST /v1/assembly-plans/{plan_id}/validate
POST /v1/assembly-plans/{plan_id}/lock
POST /v1/materialize/preview
```

交付物：

- local API server；
- API response models；
- OpenAPI docs；
- gateway error codes；
- backend smoke tests；
- minimal local run command。

本阶段不做：

- 不做 Web UI；
- 不做 MCP Server；
- 不做复杂权限；
- 不做多人部署；
- 不做 WebSocket 或实时协作。

完成标准：

- MCP Server 和前端可以只依赖 Agent Gateway API / service contract；
- API 返回结构稳定；
- 外部 Agent 所需的核心查询都能通过 API 完成；
- API 不绕过 RegistryService / QueryService / AssemblyService；
- gateway failure 有标准错误和降级语义。

---

### 15.8 Phase 4B — MCP Server for External Agents

建议周期：0.5-1 周

目标：为 Claude Code、Codex、OpenCode 等外部 Agent 提供第一版可用的动态资产发现与组装接口。

核心能力：

- `aam-mcp-server`；
- MCP tool: `list_assets`；
- MCP tool: `search_assets`；
- MCP tool: `get_asset_card`；
- MCP tool: `get_asset_dependencies`；
- MCP tool: `propose_assembly_plan`；
- MCP tool: `explain_assembly_plan`；
- MCP tool: `validate_assembly_plan`；
- timeout / retry / error semantics；
- blocked / unreviewed / sandbox_only policy handling；
- read-only + propose-only default mode；
- sample configs for Claude Code / Codex / OpenCode。

交付物：

- MCP server implementation；
- MCP tool schemas；
- Claude Code MCP config example；
- Codex MCP config example；
- OpenCode MCP config example；
- generic MCP README；
- integration smoke test；
- degraded-mode guidance。

本阶段不做：

- 默认不开放 `read_asset_full_content`；
- 默认不开放 `materialize_package`；
- 不允许外部 Agent 修改资产；
- 不允许绕过 trust / visibility / permission policy；
- 不做 host-specific Skill 的完整打包，除非作为轻量示例。

完成标准：

- Claude Code 可通过 MCP 调用 list/search/card/propose_assembly_plan tools；
- Codex 可通过 MCP 配置访问同一组 tools；
- OpenCode 至少有配置样例；
- MCP tools 默认 read-only + propose-only；
- blocked assets 不可被推荐；
- unreviewed assets 必须带 warning；
- MCP 不可用或超时时，host instructions 有明确降级行为。

---

### 15.9 Phase 5 — Host Materialization Adapters & Instruction Packs

建议周期：1 周

目标：让 approved Package Lock 真正可渲染到目标工具，并让外部 Agent 知道如何正确使用 AAM MCP。

核心能力：

- generic markdown materialization；
- generic JSON materialization；
- Codex adapter v0；
- Claude Code adapter v0；
- OpenCode adapter v0 or config example；
- materialization diff；
- materialization report；
- materialization approval gate；
- Claude Code AAM Skill；
- Codex AGENTS.md instruction pack；
- optional Codex Agent Skill if supported by active host workflow；
- OpenCode instruction/config pack；
- failure/degraded-mode instructions。

交付物：

- target adapter boundary；
- at least one production-usable target adapter；
- host instruction packs；
- materialization CLI/API integration；
- snapshot tests；
- manual host integration docs。

本阶段不做：

- 不调用外部 host API；
- 不执行 Agent；
- 不自动覆盖用户文件 without preview/approval；
- 不做所有 host 的完整支持。

完成标准：

- 给定 Package Lock，系统能 materialize 至少一个真实 host；
- materialization 结果可预览、可 diff、可审计；
- Claude Code / Codex / OpenCode 至少有正确接入说明；
- Host instruction pack 明确：先读 Asset Card，再 propose package；不编造资产；失败时降级。

---

### 15.10 Phase 6 — Web Asset Browser

建议周期：1 周

目标：从 CLI / Gateway 工具升级为可视化资产工作台的第一版。

核心能力：

- frontend app shell；
- API client；
- asset list；
- search/filter/sort；
- asset detail；
- Asset Card view；
- content preview；
- dependency / reverse dependency view；
- trust/lifecycle warning；
- package detail；
- profile detail；
- assembly plan detail；
- materialization preview entry；
- minimal rejection handling entry：Review now / Ignore once / Block asset；
- rejection reason capture；
- basic loading/error states。

交付物：

- Web UI shell；
- AssetList page；
- AssetDetail page；
- PackageDetail page；
- ProfileDetail page；
- AssemblyPlanDetail page；
- RejectionAction dialog or panel；
- API client；
- frontend smoke tests；
- UI demo workflow。

本阶段不做：

- 不做复杂 dashboard；
- 不做关系图谱可视化；
- 不做完整在线编辑；
- 不做完整资产 review form；
- 不做团队权限。

完成标准：

- 用户可以在浏览器中浏览所有 assets；
- 用户可以打开任意 asset 查看内容、metadata、trust 和 Asset Card；
- 用户可以查看一个 asset 的依赖和被依赖关系；
- 用户可以查看 package、profile 和 assembly plan 的基本结构；
- 用户拒绝 risky / unreviewed recommendation 或取消 materialization 时，可以选择 Review now / Ignore once / Block asset；
- AAM 记录 rejection reason 和用户选择，供后续推荐和治理使用；
- Web UI 不直接读文件或 registry 内部表。

---

### 15.11 Phase 7 — Dashboard & Relationship Graph MVP

建议周期：1-2 周

目标：实现项目最重要的可视化差异化能力：统计总览和关系图谱。

Dashboard 和 Graph 可以放在同一阶段，因为二者都依赖 Phase 2/4A/6 已经稳定的 stats/graph API，并且共同服务于“理解资产库整体结构”。

核心能力：

#### Dashboard

- asset count；
- package count；
- profile count；
- assembly plan count；
- package lock count；
- type distribution；
- lifecycle distribution；
- trust distribution；
- target distribution；
- source distribution；
- orphan assets；
- broken references；
- top reused assets；
- stale assets 初版；
- rejected recommendation summary。

#### Relationship Graph

- global graph；
- asset ego graph；
- profile closure graph；
- assembly plan graph；
- package lock graph；
- source/import graph nodes；
- node type filters；
- edge type filters；
- click node to detail；
- highlight orphan assets；
- highlight highly reused assets；
- highlight broken references；
- highlight blocked / unreviewed assets。

交付物：

- Dashboard page；
- stats cards and charts；
- Graph page；
- graph renderer adapter；
- graph filters；
- node detail interaction；
- graph diagnostics；
- UI demo workflow。

本阶段不做：

- 不做大型图数据库；
- 不做自动语义关系；
- 不做图谱编辑；
- 不做团队协作。

完成标准：

- 用户打开 UI 可以看到资产库整体统计；
- 用户可以通过图谱理解 package、asset、profile、assembly plan、lock、tag、target、source 的关系；
- 用户可以从任意 asset 出发查看上下游；
- 图谱能帮助识别核心资产、孤立资产、复杂 profile、风险资产和高复用资产。

---

### 15.12 Phase 8 — Asset Editing & Governance Lite

建议周期：1 周

目标：从只读浏览进入轻量治理，让用户能维护资产状态、说明、信任和关系，但不进入复杂团队审批。

核心能力：

- edit manifest metadata；
- update description/tags/lifecycle_status/visibility/trust_status；
- mark trusted / blocked / sandbox_only；
- mark deprecated / archived；
- supersedes relation；
- review notes；
- full rejection-to-governance workflow beyond MVP minimal dialog；
- impact preview before change；
- stale asset detection；
- duplicate candidate report 初版；
- governance dashboard lite。

交付物：

- metadata edit API；
- safe manifest writer；
- edit forms；
- lifecycle/trust workflow；
- review forms；
- full rejection handling UI and review flow；
- impact report；
- governance lite page；
- tests for manifest update safety。

本阶段不做：

- 不做复杂多人审批；
- 不做自动质量打分作为核心；
- 不做 Agent 自动执行 eval；
- 不让 UI 绕过 manifest 事实来源。

完成标准：

- 用户可以在 UI 中修改 asset 元数据；
- 修改会安全写回 manifest；
- 修改前可以看到影响范围；
- 用户可以逐步审查、信任、阻断、废弃、归档资产；
- 用户拒绝推荐或取消 materialization 后，可以选择 Ignore once / Review now / Block asset 等动作。

---

### 15.13 Phase 9 — Evaluation, Quality & Semantic Discovery

建议周期：1-2 周

目标：让系统从“资产治理”进入“资产质量理解”和“智能发现”。

这个阶段可以根据实际需要拆成两个子阶段：

- 9A：Evaluation & Quality；
- 9B：Semantic Search & Similarity。

核心能力：

#### Evaluation & Quality

- eval_case asset type；
- eval_case validates asset relation；
- manual eval result；
- external eval result import；
- quality report；
- profile health score；
- assembly plan feedback；
- recommendation acceptance / rejection signals。

#### Semantic Discovery

- semantic search；
- automatic tagging candidates；
- similar asset detection；
- duplicate detection；
- suggested relations；
- task-to-asset relevance；
- review-before-accept workflow。

交付物：

- EvalCase model；
- QualityReport；
- eval result import；
- semantic index；
- semantic search API/UI；
- similar_to candidate edges；
- quality and discovery UI。

本阶段不做：

- 不强制实现 Agent runtime；
- 不让 AI 自动修改正式资产；
- 不让推断关系覆盖显式关系；
- 不把质量分数伪装成绝对客观指标。

完成标准：

- 用户能知道哪些资产被 eval case 覆盖；
- 用户能看到资产质量证据；
- 用户可以语义搜索资产；
- 系统可以推荐相似资产、重复资产和潜在关系，但需要用户确认。

---

### 15.14 Phase 10 — Private Team Workspace

建议周期：2 周以上

目标：从个人 local-first 工具扩展为私有团队资产工作台。

团队模式复杂度显著高于个人模式，应该在个人工作流、Gateway、UI、图谱、materialization 和治理都稳定之后再进入。

核心能力：

- private server mode；
- users；
- workspace；
- shared registry；
- package sync/publish；
- review workflow；
- audit log；
- role-based visibility；
- shared target hosts；
- team-level gateway policy。

交付物：

- server mode；
- auth boundary；
- workspace model；
- team registry；
- sync/publish workflow；
- audit log；
- shared web UI；
- deployment doc。

本阶段不做：

- 不做公开市场；
- 不做公网社区平台；
- 不做复杂商业化功能；
- 不破坏个人 local-first 工作流。

完成标准：

- 小团队可以共享、浏览、治理和导出内部 Agent 资产；
- 团队模式是个人模式的扩展，而不是替代；
- 权限、审计、Gateway policy 和同步边界清晰。

---

### 15.15 Work Order Granularity Inside Each Phase

阶段是周级的，work order 才是适合交给 Claude Code / Codex 的粒度。

一个合格的 work order 应该满足：

- 能在一次或少数几次 AI coding 会话中完成；
- 有明确输入文件、输出文件和测试；
- 不跨越太多架构层；
- 可以被 review；
- 失败后容易回滚；
- 不需要 AI 自行重新定义产品方向。

示例：

```text
Good work order:
Implement ManifestParser and tests based on existing models and fixtures.

Bad work order:
Build the whole asset management platform.
```

每个阶段开始前，应额外产出一份短 implementation spec，包含：

1. phase goal；
2. acceptance criteria；
3. affected modules；
4. work order list；
5. testing plan；
6. known risks；
7. out-of-scope items。

---

## 16. Stage Dependency Logic

新的阶段依赖关系如下：

```text
Phase 0: Foundation & Architecture Lock
  ↓
Phase 1: Core Package System MVP
  ↓
Phase 1.5: Technical Spike Checkpoint
  ↓
Phase 2: Persistent Registry, Import Service & CLI Usability
  ↓
Phase 3: Profile Composition, Assembly Plan & Lockfile
  ↓
Phase 4A: Local Agent Gateway API
  ↓
Phase 4B: MCP Server for External Agents
  ↓
Phase 5: Host Materialization Adapters & Instruction Packs
  ↓
Phase 6: Web Asset Browser
  ↓
Phase 7: Dashboard & Relationship Graph MVP
  ↓
Phase 8: Asset Editing & Governance Lite
  ↓
Phase 9: Evaluation, Quality & Semantic Discovery
  ↓
Phase 10: Private Team Workspace
```

这个依赖顺序背后的逻辑是：

1. **先稳定资产描述，再做资产使用**  
   没有 manifest、validator、index、trust 和 Asset Card，就不应该先做 Agent Gateway、materialization、UI 或图谱。

2. **先有 content hash 和 source provenance，再做导入、锁定和导出**  
   资产导入、变更检测、Package Lock、materialization 快照和复现都依赖 hash 与来源信息。

3. **先有 Profile closure 和 Assembly Plan，再做 MCP**  
   MCP Server 不应自己实现组装逻辑。它应该包装已经稳定的 AssemblyService / RegistryService。

4. **先有 Agent Gateway API，再有 MCP Server**  
   MCP 是外部 Agent 协议层；底层 gateway contract 应先稳定。

5. **先有 MCP / materialization，再做 Web UI**  
   本项目的新差异化是 Agent-facing discovery and assembly，因此 Agent Gateway 应前移，Web UI 后移。

6. **Core MVP 需要最小拒绝处理，但完整编辑治理后置**  
   Phase 6 应提供 Review now / Ignore once / Block asset 的最小 rejection handling，避免拒绝成为死胡同；编辑 manifest、review form、状态迁移和完整治理面板仍应晚于只读浏览。

7. **先有 graph data，再有 graph UI**  
   图谱可视化依赖 nodes/edges 数据模型、graph query 和基础前端框架。

8. **先个人 local-first，再团队 workspace**  
   团队模式是个人模式的扩展，不应反过来拖累早期本地工作流。

需要特别注意：

- Phase 1 虽然只是本地核心系统，但必须 source-aware、hash-aware、trust-aware、asset-card-aware、graph-aware。
- Phase 2 正式引入 import service，因为导入是资产进入系统的核心入口。
- Phase 3 是 Profile 与 Agent Assembly 的共同底座。
- Phase 4A/4B 把 Gateway contract 与 MCP protocol 拆开，降低协议集成风险。
- Phase 5 负责把锁定结果真正写入目标宿主。
- Phase 6 后才进入 Web UI，是因为当前项目核心差异不是漂亮 UI，而是外部 Agent 可安全消费资产库。

---

## 17. What Must Be Stable From Day One

以下设计一旦确定，后续不要轻易变更：

1. Package / Asset / Profile 是核心概念。
2. Asset Card 是外部 Agent 消费资产前的安全摘要投影。
3. Discovery Request / Assembly Plan / Package Lock / Materialization 是 Agent-facing 资产消费路径的核心概念。
4. Profile 是长期人工治理基线；Assembly Plan 是任务级动态组合建议。
5. Manifest 是事实来源。
6. Registry 是索引缓存和查询基础。
7. Relationship Graph 是系统长期核心能力，不是附属功能。
8. Agent Gateway 是外部 AI Agent 的受控接口层。
9. MCP Server 是动态能力接口；Skill / AGENTS.md / Host Instruction Pack 是行为引导层。
10. Import 是正式 workflow，不是临时脚本。
11. Source provenance 必须从导入阶段开始保留。
12. 本地导入和 GitHub 导入必须共享 SourceAdapter 抽象。
13. GitHub 导入必须 pin 到 commit SHA。
14. `content_hash` 必须存在，用于 provenance、registry、Package Lock、materialization snapshot 和 change detection。
15. `content_hash` 是否参与 primary identity 另行决策。
16. 系统不直接执行 Agent。
17. 系统不负责 pip/npm 风格依赖安装。
18. 系统默认 local-first / private-first。
19. Asset identity 不直接绑定文件路径。
20. 依赖关系必须显式声明。
21. 资产 lifecycle status 和 trust status 必须从早期引入。
22. tag、target、visibility、lifecycle status、trust_status、depends_on、source、permission metadata 不能等到 UI 阶段才补。
23. blocked 资产不可被推荐、组装或 materialize。
24. unreviewed 资产进入候选或计划时必须显式 warning。
25. 前端、CLI、MCP、图谱都应通过 registry/query/assembly service 获取数据，而不是各自扫描文件。
26. Agent Gateway failure 时必须 fail closed for asset access, fail soft for task execution。
27. 用户拒绝推荐或取消 materialization 后，应进入 rejection-to-governance loop。
28. 开发流程可以强耦合 GitHub，但产品核心架构不应强耦合 GitHub。

---

## 18. First Implementation Boundary

第一批代码对应 Phase 1：**Core Package System MVP**。

它不是最终产品，也不是完整 CLI 工具，而是整个项目的可运行底座。

第一批实现范围：

```text
package directory spec
package.yaml manifest schema
Package / Asset / Profile models
Asset Card minimal model
TrustStatus / LifecycleStatus models
Permission metadata model
basic Source provenance model
manifest parser
validator
reference resolver
content hash computation
in-memory registry
basic graph projection
example packages / fixtures
minimal CLI: init / validate / index / list / show
```

第一批代码必须保留未来 UI、统计、导入、Agent Gateway、MCP、Assembly、Materialization 和图谱需要的基础字段：

- package id / version；
- asset id / type / path；
- asset lifecycle status；
- asset trust status；
- asset visibility；
- tags；
- target_hosts；
- source provenance；
- profile includes；
- asset depends_on；
- permission metadata；
- Asset Card projection fields；
- content hash；
- indexed timestamp；
- graph nodes / edges。

第一批明确不做：

- 不做完整 GitHub importer；
- 不做复杂 ImportRun 持久化；
- 不做持久化 registry DB；
- 不做完整 HTTP API；
- 不做 MCP Server；
- 不做 Web UI；
- 不做 profile export / materialization system；
- 不做 target-specific adapter；
- 不做资产编辑；
- 不做团队协作。

这可以避免第一阶段过重，同时确保后续不会因为数据模型太窄而返工。

---

## 19. Success Criteria

### 19.1 Phase 1 Success Criteria

Phase 1 成功的标准是完成最小资产管理底座：

1. 用户能创建一个资产包。
2. 用户能把 prompt、agent、skill、MCP config 等资产登记进 manifest。
3. 系统能解析 manifest 并生成 typed models。
4. 系统能校验资产包是否自洽。
5. 系统能识别 broken references、missing files 和 dependency cycles。
6. 系统能计算 asset content hash。
7. 系统能构建 in-memory registry。
8. 系统能查询并展示资产列表和单个 asset 详情。
9. 系统能生成 Asset Card projection。
10. 系统能输出初版 graph nodes/edges。
11. registry 中包含 source provenance、content hash、trust status、permission metadata 和 indexed timestamp。
12. 核心逻辑有 fixtures 和测试覆盖。

### 19.2 Product Core MVP Success Criteria

产品 Core MVP 应至少完成 Phase 1-6，并包含 minimal Agent Gateway 和 minimal rejection handling 能力：

1. 用户能通过 CLI 管理本地资产包。
2. 用户能从本地目录和 GitHub 公共仓库导入资产。
3. 用户能定义 Profile。
4. 用户能查看任意 asset 的 Asset Card。
5. 系统能根据 task + target_host 生成 Assembly Plan。
6. 系统能基于已有 Profile 生成 Assembly Plan，并展示 profile_delta。
7. 系统能生成 Package Lock。
8. 系统能 materialize 至少一个真实目标 host。
9. 外部 Agent 能通过 MCP 读取 list/search/card/propose_assembly_plan tools。
10. MCP tools 默认 read-only + propose-only。
11. 用户能在 Web UI 中浏览任意 asset。
12. 用户能看到 trust warning、dependency closure 和 materialization preview。
13. 用户拒绝 risky / unreviewed recommendation 或取消 materialization 时，能看到 Review now / Ignore once / Block asset 等下一步动作。
14. AAM 能记录 rejection reason 和用户选择，供后续推荐和治理使用。
15. 导出 / materialization 结果可复现、可审计、可 diff。
16. 系统仍然保持 local-first / private-first。

Core MVP 不要求完整 Dashboard 与 Relationship Graph UI；这属于 MVP+。

### 19.3 Product MVP+ Success Criteria

产品 MVP+ 应至少完成 Phase 7 的 Dashboard & Relationship Graph MVP：

1. 用户能看到资产统计 dashboard。
2. 用户能查看 asset ego graph、profile closure graph、source lineage graph 或 assembly graph。
3. 图谱能帮助识别核心资产、孤立资产、复杂 Profile、风险资产和高复用资产。
4. dashboard 能展示 rejected recommendation summary 和 basic trust / lifecycle distribution。

### 19.4 Long-term Success Criteria

长期成功的标准是：

1. 用户能在前端浏览任意 asset。
2. 用户能看到完整资产统计和健康状态。
3. 用户能通过关系图谱理解资产库结构。
4. 用户能从任意 asset 查看上下游依赖和影响范围。
5. 用户能追踪资产来源、导入版本和 GitHub commit pinning。
6. 用户能把资产组合稳定 materialize 给不同 Agent 工具。
7. 外部 Agent 能安全发现资产、读取 Asset Card、请求 Assembly Plan 并解释选择理由。
8. 用户能治理资产质量、版本、信任、复用和废弃关系。
9. 系统能从个人本地工作流自然扩展到私有团队工作流。

---

## 20. Rejection-to-Governance Loop

当用户因为 trust warning 取消 materialization，或拒绝外部 Agent 推荐的资产时，系统不应把拒绝视为终点。

拒绝应该成为治理入口。

典型场景：

- 用户拒绝 unreviewed asset 进入 profile；
- 用户取消包含 risky MCP/tool asset 的 Assembly Plan；
- 用户拒绝 Agent 推荐的某个资产；
- 用户因为 blocked / sandbox_only warning 取消 materialization；
- 用户多次忽略同一个推荐资产。

产品应引导用户选择明确下一步：

- `Ignore once`：仅本次忽略，不改变资产状态；
- `Review now`：进入资产审查页，查看来源、内容、依赖、权限和风险；
- `Mark as trusted`：审查后提升为 trusted；
- `Mark as blocked`：明确阻止未来推荐、组装和导出；
- `Mark as sandbox_only`：允许实验性使用，但不能进入默认 materialization；
- `Deprecate asset`：资产仍可追溯，但不再推荐；
- `Suppress for this context`：不改变全局状态，只在当前 project/profile/task 类型下不再推荐。

MVP 最小闭环：

```text
User rejects unreviewed/risky asset
  → AAM records rejection reason
  → AAM offers Review now / Ignore once / Block asset
  → Future recommendations use this signal
```

---

## 21. Open Questions

这些问题进入后续专项 spec，不在基石文档中一次性解决：

1. package lock 文件字段如何设计？
2. 跨 package dependency 的最终 URI 格式是什么？Phase 1/3 前至少应采用临时可解析格式，例如 `asset:<asset_id>`、`asset:<package_id>/<asset_id>`、`asset:<package_id>/<asset_id>@<version>`。
3. registry storage 最终采用 SQLite、DuckDB、JSON 还是其他方案？
4. MCP server 技术栈和 tool schema 具体如何设计？
5. Agent Gateway API 是否直接暴露 HTTP，还是仅作为内部 service contract？
6. 图谱前端最终使用 React Flow、Cytoscape.js、Sigma.js、G6 还是其他库？
7. asset schema 是否按 type 细分？
8. target adapter 如何组织？
9. secret/env/config override 如何处理？
10. profile 是否支持 inheritance？
11. Assembly Plan 是否支持 inheritance 或 plan composition？
12. 如何处理同名 asset 冲突？
13. `content_hash` 是否参与 Asset primary identity？
14. 如何绑定 Git tag/release 与 package version？
15. 自动语义标签和 similar_to 关系是否需要 embedding？
16. 团队模式是否需要中心 registry server？
17. Web UI 是否支持编辑，还是只浏览到 Phase 8？
18. Local import 的默认模式应该是 adopt 还是 copy/snapshot？
19. GitHub import 是否需要支持 private repositories？
20. GitHub import 是否通过 Git CLI、GitHub API，还是二者都支持？
21. Imported Package 的 wrapper manifest 应该存放在哪里？
22. ImportRun 是否需要进入 registry persistence 的第一版？
23. Phase release 应该使用 `phase-*` tag 还是 semver tag？
24. 未来团队模式是否要求 registry storage 从一开始支持同步或迁移？
25. Asset Card 是只存 manifest 字段，还是允许系统生成缓存？
26. 外部 Agent 是否可以读取 full content？如果可以，最小 approval/policy 是什么？
27. materialize_package 是否允许 MCP 调用？如果允许，如何进行用户确认？
28. Rejection reason taxonomy 如何设计？
29. repeated rejection 是否会降低推荐分，还是只提示用户治理？
30. context_cost 如何估算、缓存和更新？

---

## 22. Phase Spec Template

每个 Phase 开始前，应创建独立的 implementation spec，格式如下：

```markdown
# Phase N Implementation Spec

## Goal

## Scope

## Non-goals

## Affected Modules

## Data Models

## Public Interfaces

## Work Orders

## Acceptance Criteria

## Testing Plan

## Risks

## Review Checklist
```

Phase spec 是工程执行文档；本 foundation spec 是架构宪章。两者不应混淆。

对于涉及 Agent Gateway 的阶段，还应额外包含：

```markdown
## Agent-facing Contract

## Tool / API Schema

## Policy Gates

## Failure and Degraded Mode

## Host Integration Notes
```

---

## 23. Final Definition

Agent Asset Management 是一个 local-first、private-first、source-aware、trust-aware、graph-aware 的 Agent Asset Registry 与 Agent-facing Discovery and Assembly Layer，用于结构化管理、导入、浏览、统计、关系建模、治理、发现、组装、锁定和 materialize 个人或团队积累的 Agent 能力资产。

它以 Package / Asset / Profile / Asset Card / Assembly Plan / Package Lock 为核心，以 Manifest 为事实来源，以 Registry 为查询基础，以 Agent Gateway 为外部 AI Agent 的受控接口，以 Relationship Graph 为长期差异化能力，以 MCP Server 作为动态能力接口，以 Skill / AGENTS.md / Host Instruction Pack 作为行为引导层，以 GitHub PR workflow 作为推荐开发治理方式。

它不执行 Agent、不安装第三方依赖、不提供公开资产市场、不默认暴露完整资产内容，也不把产品核心架构硬编码到 GitHub。
