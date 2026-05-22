# Agent Asset Management Product Brief

## 1. Status

Draft v0.3.2

本文档是 Agent Asset Management 项目的产品简报，用于补充 Foundation & Roadmap Spec。

Foundation & Roadmap Spec 回答：

> 这个系统的长期架构边界、核心模型、阶段路线和实现优先级是什么？

Product Brief 回答：

> 用户为什么需要这个产品？第一次使用时应该获得什么价值？哪些能力应该优先服务核心用户路径？外部 AI Agent 为什么需要接入这个资产库？

本文档不是实现 spec，不定义数据库表、API 细节、前端组件或 CLI 参数。它定义产品定位、核心用户、核心问题、产品承诺、MVP 范围和成功指标。

v0.3.2 在 v0.3.1 的基础上完成四项一致性修正：

- 明确 Core MVP 与 MVP+ 的范围，避免将完整 Dashboard / Graph 过早压入核心 MVP；
- 将 rejection-to-governance 的最小闭环纳入 Core MVP，但把完整治理编辑留到后续阶段；
- 修正 Manifest / Registry 的事实源关系，避免把 Registry 误写为 source of truth；
- 统一 Assembly 相关语言，减少 package / bundle / lockfile 的概念混用。

---

## 2. Product Thesis

随着 AI coding、agent workflow、MCP、rules、skills、sub-agents、PR-based coding agents 和 host-specific instructions 的发展，用户正在积累越来越多的 Agent 能力资产。

这些资产通常分散在：

- 本地目录；
- GitHub 仓库；
- 项目根目录的 agent instructions；
- Claude Code / Codex / Cursor / ChatGPT / OpenCode 等工具配置；
- MCP server configs；
- prompt 文件；
- workflow templates；
- sub-agent definitions；
- skills；
- scripts；
- 聊天记录和临时笔记中。

问题不是用户没有资产，而是用户逐渐不知道：

- 自己有哪些资产；
- 哪些资产仍然可用；
- 哪些资产可以复用；
- 哪些资产已经过时；
- 哪些资产可信；
- 哪些资产适合某个任务；
- 哪些资产能被某个 host 使用；
- 哪些资产被哪些 profile、package 或项目使用；
- 修改一个核心 asset 会影响什么；
- 如何把一组资产稳定导出给某个 AI 工具；
- 外部 AI Agent 在执行任务前，如何知道本地资产库里有哪些能力可用。

Agent Asset Management 的产品机会在于：

> 把散落的 Agent 能力资产变成一个本地优先、私有优先、可浏览、可搜索、可组合、可导出、可治理、可被外部 AI Agent 安全消费的 Agent Asset Registry。

因此，AAM 不只是一个人类用户使用的资产工作台，也应该是一个：

> Private Agent Asset Registry with Agent-facing Discovery and Assembly Layer.

也就是说：

```text
Human manages assets.
External Agent consumes assets.
AAM governs discovery, assembly, trust, dependency, rendering, and audit.
```

---

## 3. Product Positioning

Agent Asset Management 是一个本地优先、私有优先的 Agent Asset Registry 与 Agent-facing Assembly Layer。

它帮助用户把 prompts、skills、agents、MCP configs、rules、workflows、scripts、templates、profiles、plugins 和 bundles 等资产沉淀为可索引、可验证、可组合、可导出、可审计的私有资产库。

在此基础上，AAM 进一步提供 Agent Gateway，使 Claude Code、Codex、OpenCode、Cursor 或其他 MCP-compatible clients 等外部 AI Agent 可以在执行任务前：

- 查询本地资产库；
- 发现可用资产；
- 读取安全的 Asset Card；
- 评估资产与当前任务的匹配度；
- 请求生成 task-specific assembly plan；
- 解释被选中和被排除的资产；
- 在用户确认或 policy 允许后，使用 materialized bundle。

AAM 的产品边界是：

> AAM 是资产注册表、发现层、组装控制面和导出层，不是 Agent runtime。

外部 Agent 负责执行任务；AAM 负责治理它能发现什么、读取什么、请求什么、组装什么、导出什么。

AAM 支持两条互补的资产组合路径：

```text
Human-curated Profile:
  长期、稳定、场景化的资产基线。

Agent-generated Assembly Plan:
  动态、任务特定、可解释的资产组合建议。
```

Assembly Plan 可以从零生成，也可以基于某个已有 Profile 生成。当用户或外部 Agent 提供 base profile 时，AAM 应把 Profile 视为基线，只在当前任务确实需要时动态添加、排除或覆盖资产。

---

## 4. Target Users

### 4.1 Primary Human User: Heavy AI Coding User

这类用户长期使用 Claude Code、Codex、Cursor、ChatGPT、OpenCode 等工具辅助开发。

他们已经积累了大量：

- coding rules；
- project instructions；
- code review prompts；
- architecture review prompts；
- debugging workflows；
- MCP configs；
- reusable agent roles；
- task-specific skills；
- host-specific configuration snippets。

他们的痛点是：资产增长速度快于管理能力。

他们最需要：

- 快速找到已有资产；
- 避免重复创造类似 prompts/rules；
- 把成熟资产迁移到新项目；
- 理解某个规则或工具配置被哪些 profile 使用；
- 让外部 AI Agent 在任务执行前自动发现这些成熟资产。

### 4.2 Primary Machine User: External AI Agent / Coding Agent

这类用户不是人，而是外部 AI 工具中的 agent。

代表包括：

- Claude Code；
- Codex；
- OpenCode；
- Cursor / Copilot；
- Gemini CLI；
- Generic MCP-compatible clients。

它不是资产所有者，也不是资产治理者，但它是资产消费者。

它需要在执行任务时回答：

- 当前本地资产库中有哪些资产可用？
- 哪些资产与当前任务相关？
- 哪些资产适合当前 host？
- 哪些资产可信？
- 哪些资产需要权限或存在风险？
- 需要哪些依赖闭包？
- 当前任务应该组装成什么 package / profile / bundle？

外部 Agent 不能绕过 AAM 的 trust、visibility、permission、dependency 和 materialization policy。

它应该通过 Agent Gateway 请求资产发现和组装，而不是自己随意读取和拼装资产内容。

### 4.3 Secondary Human User: Personal Researcher / Builder

这类用户在多个研究或开发项目中复用 AI 资产。

例如：

- 量化研究项目；
- 论文写作项目；
- 数据分析项目；
- 后端开发项目；
- 自动化脚本项目；
- 私人工具链项目。

他们需要针对不同场景组合不同 Agent profile，并希望这些组合可以被自己或外部 coding agent 复用。

### 4.4 Future User: Small Private Team

这类用户属于小型技术团队或研究团队。

他们需要共享内部 Agent 资产，但不需要公开市场或重型企业平台。

他们未来会需要：

- 团队资产浏览；
- review workflow；
- shared profiles；
- audit log；
- usage tracking；
- 权限和可见性控制；
- 团队内部 Agent Gateway；
- 资产信任与使用反馈闭环。

团队用户不是 MVP 的第一目标，但产品架构不能堵死团队演进。

---

## 5. Core Product Problems

### 5.1 Inventory Problem

用户不知道自己有哪些 Agent 资产。

这些资产分散在不同工具、项目和仓库中，缺少统一 inventory。

产品应解决：

> 我到底有哪些 prompts、rules、skills、agents、MCP configs、workflows、profiles 和 host instructions？

### 5.2 Discovery Problem

用户知道自己曾经写过类似资产，但找不到。

产品应解决：

> 我之前是不是写过一个 Polars 性能优化 rule？是不是有一个 code review agent？哪个项目里有好用的 MCP config？

### 5.3 Agent Consumption Problem

外部 AI Agent 执行任务时，不知道本地有哪些资产可用。

它只能依赖当前上下文、项目文件和临时指令，很难主动利用用户长期积累的私有资产。

产品应解决：

> 当 Claude Code / Codex / OpenCode 接到一个任务时，它能否先询问 AAM：当前任务有哪些可用资产？应该组装哪些资产？哪些资产不能用？

### 5.4 Assembly Problem

即使资产可以被搜索到，用户或外部 Agent 仍然需要判断哪些资产应该一起使用。

产品应解决：

> 面向当前任务、当前 host、当前权限限制和当前上下文预算，应该把哪些 assets 组装成一个 package / profile / bundle？

### 5.5 Reuse Problem

资产难以跨项目复用。

用户往往通过复制粘贴迁移规则和配置，导致漂移、重复和版本混乱。

产品应解决：

> 我能不能把成熟资产组合成 profile，并稳定渲染给新项目、新任务或新工具？

### 5.6 Provenance Problem

用户不知道资产从哪里来、基于哪个版本、是否可信。

尤其是 GitHub 导入、MCP/tool 类资产和外部生成的 prompt/skill，来源和版本锚点非常重要。

产品应解决：

> 这个 asset 是我自己写的、本地导入的，还是从 GitHub 某个 commit 导入的？我能否追踪它的来源？

### 5.7 Impact Problem

用户修改一个核心 asset 前，不知道影响范围。

产品应解决：

> 如果我修改这个 coding rule，会影响哪些 profile、exports、packages、host configs 和项目？

### 5.8 Trust and Safety Problem

从外部导入的 assets 可能存在安全、质量或信任问题。

尤其是：

- MCP server；
- shell command；
- tool config；
- prompt injection 风险内容；
- 涉及 secret/env 的配置；
- 未审查的 GitHub 资产；
- external agent 请求读取或 materialize 的资产。

产品应解决：

> 哪些资产是可信的？哪些只是导入但未审查？哪些只能 sandbox 使用？哪些资产不能被外部 Agent 静默读取或导出？

---

## 6. Product Promise

Agent Asset Management 给用户的承诺是：

> 你可以把分散的 Agent 资产导入一个私有资产库，快速知道自己拥有什么，找到可复用资产，理解资产关系，组合成 profile 或 package，并稳定导出给不同 AI 工具。

进一步，AAM 给外部 AI Agent 的承诺是：

> 你可以通过受控接口发现本地资产库中的可用能力，读取安全摘要，评估任务匹配度，并请求 AAM 生成当前任务下最合适的资产组装方案。

这个承诺包含七个关键词：

1. **Import**：把已有资产带进系统。
2. **Inventory**：形成统一资产清单。
3. **Discover**：让人和 Agent 都能快速搜索和浏览资产。
4. **Understand**：理解依赖、来源、信任、权限、上下文成本和影响范围。
5. **Assemble**：为某个任务、host 和约束组装合适资产。
6. **Render / Export**：把 profile/lock 渲染到目标工具。
7. **Govern**：持续维护资产信任状态、生命周期、来源、使用情况和风险。

---

## 7. Core Product Loops

AAM 有两个互相加强的核心闭环。

### 7.1 Human Asset Management Loop

```text
Import assets
  → Index and show inventory
  → Search / browse assets
  → Inspect asset detail and relationships
  → Create or refine profile
  → Preview / export profile to target tool
  → Reuse profile in real work
  → Return to update, govern, and inspect impact
```

这个闭环服务人类用户。

### 7.2 Agent-facing Discovery and Assembly Loop

```text
External Agent receives a task
  → Query AAM Agent Gateway
  → Discover relevant assets
  → Inspect Asset Cards
  → Request an Assembly Plan
  → Explain selected / excluded assets and risks
  → User or policy approves
  → AAM resolves, locks, and materializes package
  → External Agent uses the package in real work
  → AAM records usage and feedback
```

这个闭环服务外部 AI Agent。

两个闭环共享同一个 Registry Core。人类负责管理和治理资产；Agent 负责在任务中请求和使用资产；AAM 负责保证资产选择、组装、导出和审计过程可控。

### 7.3 Profile-based Assembly Loop

Profile 和 Assembly Plan 不应该成为两套割裂的组合机制。更合理的闭环是：

```text
User or Agent selects a base Profile
  → AAM treats the Profile as the baseline
  → Agent Gateway discovers task-specific delta assets
  → AAM proposes additions / removals / overrides
  → Assembly Plan explains the delta and risks
  → User or policy approves
  → AAM resolves, locks, and materializes the result
```

这让用户可以维护长期稳定的场景化 Profile，同时允许外部 Agent 针对当前任务做动态补充。

产品原则：

> Profile answers what I usually use for this scenario. Assembly Plan answers what this agent should use for this task right now.

---

## 8. First-use Experience

用户第一次使用产品时，最重要的不是看到完整 dashboard 或复杂图谱，而是快速获得确定感：

> 系统已经识别出我的 Agent 资产，并让我知道它们在哪里、是什么、能怎么用。

### 8.1 Ideal First Human Session

第一次使用路径应尽量是：

```text
1. Create local workspace
2. Import from local folder or GitHub repository
3. System scans and indexes assets
4. User sees asset inventory
5. User opens an asset detail page
6. User sees content, source, tags, dependencies, trust status, and related profiles
7. User creates or selects a profile
8. User previews target-specific rendering
```

### 8.2 Ideal First Agent Gateway Session

当用户把 AAM 接入 Claude Code / Codex / OpenCode 后，第一条 Agent-facing 路径应尽量是：

```text
1. Configure AAM MCP server or host instruction pack
2. External Agent receives a task
3. Agent calls AAM to search relevant assets
4. AAM returns Asset Cards and candidate assets
5. Agent requests an Assembly Plan
6. AAM returns selected assets, excluded assets, warnings, and rationale
7. Agent explains the plan to the user
8. User approves or rejects materialization
```

### 8.3 First Moment of Value

第一价值时刻不是“安装成功”，而是：

> 用户看到一张清晰的资产清单，并发现系统找到了自己以前散落的 Agent 能力资产。

### 8.4 First Agent-facing Value Moment

Agent-facing 的第一价值时刻是：

> 外部 Agent 在执行真实任务前，主动发现并推荐了用户本地已有的相关资产，而不是要求用户手动复制 prompt、rules 或 config。

### 8.5 First Wow Moment

第一 wow moment 是：

> 用户点击一个 asset，系统展示它的来源、依赖、被哪些 profile 使用、是否可信，以及修改它可能影响什么。

Agent-facing 的 wow moment 是：

> Claude Code / Codex / OpenCode 可以解释：为什么当前任务应该使用这些 assets，为什么另一些 assets 被排除，以及哪些风险需要用户确认。

关系图谱可以成为 wow moment，但不应该是第一价值的前提。

---

## 9. MVP Product Scope

产品 MVP 不等于 Phase 1。

v0.3.2 将 MVP 明确拆成两个层级：

```text
Core MVP:
  完成人类资产管理 + 外部 Agent 发现与组装 + 至少一个真实 host materialization 的最小闭环。

MVP+:
  在 Core MVP 之上加入完整 Dashboard 与 Relationship Graph 体验。
```

Core MVP 至少需要完成两个最小闭环：

1. 人类用户可以导入、浏览、搜索、组合、锁定并 materialize 资产。
2. 外部 Agent 可以通过受控接口发现资产、读取 Asset Card、请求 Assembly Plan，并在失败时安全降级。

Core MVP 应覆盖以下价值能力：

1. 本地资产包管理；
2. 本地目录导入；
3. GitHub 公共仓库导入；
4. 资产 inventory；
5. 搜索和过滤；
6. asset detail；
7. agent-readable Asset Card；
8. profile composition；
9. Assembly Plan；
10. Package Lock / locked usage snapshot；
11. 至少一个真实 target rendering / materialization；
12. Agent Gateway MVP；
13. MCP read-only / propose-only 接入；
14. trust warning 和 blocked asset 阻断；
15. Gateway failure / degraded mode；
16. rejection-to-governance 的最小闭环。

其中，rejection-to-governance 在 Core MVP 中只要求最小可用闭环：

```text
User rejects risky / unreviewed recommendation
  → AAM records rejection reason
  → UI or Agent response offers Review now / Ignore once / Block asset
  → future recommendation can avoid repeated bad suggestions
```

完整的资产编辑、review form、状态迁移、governance dashboard 和长期治理工作流可以进入 Core MVP 之后的治理阶段。

完整 Dashboard 与 Relationship Graph 是 MVP+，不是 Core MVP 的硬性前提。Core MVP 可以保留 graph JSON、dependency / reverse dependency view、profile closure view 和 basic stats，但不要求完整图谱可视化工作台。

换言之，产品 Core MVP 应大致覆盖 Foundation & Roadmap Spec 中 Registry、Import、Search、Profile、Assembly、Gateway、Host Materialization、Web Asset Browser 和 minimal rejection handling 的最小闭环。Dashboard / Relationship Graph 属于 MVP+ 差异化增强。

---

## 10. Daily-use Features vs Wow Features

### 10.1 Daily-use Features

这些功能是用户持续使用产品的主要原因：

- 搜索 assets；
- 按 type/tag/source/target/status/trust 过滤；
- 查看 asset 内容；
- 查看 Asset Card；
- 查看 asset 来源；
- 查看 asset 被哪些 profile 或 package 使用；
- 创建和调整 profile；
- 生成和解释 Assembly Plan；
- 导出或 materialize profile/lock；
- 查看 stale / orphan / broken assets；
- 修改前查看影响范围；
- 让外部 Agent 发现当前任务相关资产。

Daily-use 功能要优先做到稳定、快速、清晰。

### 10.2 Wow Features

这些功能更容易让用户感到产品有差异化：

- 外部 Agent 自动请求 task-specific package；
- Agent 解释 selected / excluded assets；
- 全局关系图谱；
- asset ego graph；
- profile closure graph；
- source lineage graph；
- change impact graph；
- duplicate asset detection；
- semantic search；
- 自动推荐相似资产；
- package health score；
- usage feedback-driven recommendation。

Wow 功能不能牺牲 daily-use 稳定性。

图谱和智能推荐尤其不能变成纯展示功能；它们必须回答具体问题。

---

## 11. Search-first and Discovery-first Product Bias

资产管理产品的高频入口通常不是 dashboard，而是 search。

用户更常见的问题是：

- 我有没有写过类似 prompt？
- 哪个项目里有这条 rule？
- 有没有适合 code review 的 agent？
- 哪些 assets 和 MCP 相关？
- Claude Code 和 Cursor 是否使用了同一套 instructions？
- 当前任务应该使用哪些本地资产？

因此，Asset Browser 应该被设计成一个私有 Agent 资产搜索引擎。

Agent Gateway 则应该被设计成一个外部 AI Agent 可调用的私有资产发现与组装入口。

搜索能力优先级：

1. keyword search；
2. type filter；
3. tag filter；
4. source filter；
5. target filter；
6. status filter；
7. trust filter；
8. dependency / reverse dependency filter；
9. full-text search；
10. task-intent search；
11. semantic search。

Semantic search 可以后置，但 full-text search 和 metadata-based discovery 应尽早进入产品规划。

### 11.1 Assisted Discovery

除了主动搜索，产品还应该支持低成本的辅助发现。

主动搜索回答的是：

> 用户知道自己想找什么，然后输入关键词。

辅助发现回答的是：

> 用户正在浏览一个 asset，系统顺手告诉他还有哪些相关资产值得看。

Agent-facing discovery 回答的是：

> 外部 Agent 面对一个任务时，系统告诉它有哪些资产适合当前任务。

辅助发现不需要一开始依赖 embedding 或语义搜索，可以优先基于显式 metadata 和 graph relations 实现。

典型推荐包括：

- 同一 tag 下的其他 assets；
- 同一 tag 下最常用的 profiles；
- 使用同一个 MCP server 的 assets；
- 依赖同一个 asset 的 profiles；
- 来自同一个 source/import run 的 assets；
- 面向同一个 target 的常用 assets；
- 与当前 asset 共享 depends_on 的 assets；
- 与当前 asset 同 type 且高复用的 assets；
- 与当前 task intent 匹配且 trust 状态安全的 assets。

辅助发现的产品价值是：

1. 降低用户记忆负担；
2. 提高已有资产复用率；
3. 在 semantic search 实现前提供有用的相关性推荐；
4. 让 asset detail page 从静态详情页变成探索入口；
5. 让外部 Agent 在执行任务前能主动使用私有资产库。

产品原则：

> Asset detail page 不应只是展示当前 asset，还应该帮助用户发现上下文相关的其他资产。Agent Gateway 不应只是暴露资产列表，还应该帮助外部 Agent 请求 task-specific assembly。

---

## 12. Import Product Requirements

导入是资产进入系统的第一入口。

产品上，导入流程必须让用户清楚知道：

- 导入了什么；
- 从哪里导入；
- 是否生成 package；
- 是否生成 wrapper manifest；
- 是否生成 Asset Card；
- 有哪些 warnings；
- 哪些 assets 未识别；
- 哪些 assets 需要手动补充 metadata；
- GitHub 导入 pin 到哪个 commit；
- 是否存在潜在风险；
- 外部 Agent 是否可以发现该资产。

### 12.1 Local Import

本地导入应优先服务已有资产整理。

用户不应该一开始就被迫重构目录。

合理体验：

```text
Import local folder
  → system detects candidate assets
  → user reviews generated manifest and Asset Card
  → user accepts / edits / skips
  → system indexes package
```

### 12.2 GitHub Import

GitHub 导入应优先服务公共资产采集和复用。

合理体验：

```text
Import GitHub repo/path/ref
  → resolve ref to commit SHA
  → detect candidate assets
  → generate imported package wrapper
  → mark assets as unreviewed by default
  → user reviews and promotes trusted assets
```

### 12.3 Imported Asset Trust State

外部导入资产默认不应直接视为 trusted。

建议状态：

```text
trusted
unreviewed
sandbox_only
blocked
needs_manual_review
```

早期可以只实现 `trusted / unreviewed / blocked`，但产品模型应保留扩展空间。

### 12.4 Agent Visibility after Import

资产导入后，不应默认向外部 Agent 暴露完整内容。

合理策略：

```text
trusted asset:
  可出现在搜索结果中，可展示 Asset Card，可按 policy preview/full read/materialize。

unreviewed asset:
  可出现在候选中，但必须带 warning；默认不应静默进入 package。

blocked asset:
  不应被推荐，不应被 materialize，不应被外部 Agent 使用。
```

---

## 13. Asset Card Product Requirements

Asset Card 是面向外部 Agent 的安全摘要层。

它不是完整 manifest，也不是完整 asset content，而是一个可被 Agent 快速读取和评估的投影。

Asset Card 应帮助外部 Agent 判断：

- 这个资产是什么；
- 适合什么任务；
- 支持哪些 host；
- 依赖什么；
- 是否可信；
- 权限风险是什么；
- 上下文成本大概是多少；
- 是否适合进入当前 package。

Asset Card 应至少表达：

```text
id
type
version
title
summary
intended_use
tags
target_hosts
dependencies
trust_status
lifecycle_status
permission_risk
quality_status
estimated_context_cost
```

Asset Card 的生成责任应明确：

- 硬字段应来自 manifest、source provenance、static detector 或用户审查，例如 `trust_status`、`permission_risk`、`target_hosts`、`dependencies`、`estimated_context_cost`；
- 软字段可以由 manifest 显式提供，也可以由 indexer 根据安全摘要生成，例如 `summary`、`intended_use`、`input_context`、`output_capabilities`；
- `trust_status` 和 permission metadata 不能由 LLM 凭内容质量臆测；
- 自动生成的 Asset Card 必须经过 redaction，不得暴露 secret、token、API key、cookie、私密绝对路径或完整高风险脚本内容。

产品原则：

> 外部 Agent 应先读取 Asset Card，再决定是否请求 Assembly Plan。它不应默认直接读取完整 asset content。

---

## 14. Profile, Assembly Plan, Package Lock, and Export Product Requirements

Profile、Assembly Plan、Package Lock 和 Materialized Bundle 是用户把资产变成实际生产力的核心桥梁。

用户真正需要的不是“导出文件”，而是：

> 把一组资产渲染成目标工具可以直接消费的 Agent workspace bundle。

外部 Agent 真正需要的不是“任意读取资产”，而是：

> 请求 AAM 为当前任务生成一个安全、可解释、可审计的 Assembly Plan。

### 14.1 Concept Relationship

AAM 支持两种互补的组合路径。

第一条路径是 human-driven Profile composition。Profile 是长期、稳定、人工治理的场景化资产基线，例如 Python code review、quant research、paper writing、MCP-heavy project setup。

第二条路径是 agent-driven Assembly。Assembly Plan 是 AAM 响应外部 Agent discovery request 后生成的任务级组合建议。它可以从零生成，也可以基于已有 Profile 生成。

当提供 base Profile 时，Assembly Plan 应该把 Profile 视为 baseline，并只在当前任务需要时提出 delta：

- add：加入任务特定资产；
- remove：排除不适合当前任务或当前 host 的资产；
- override：用更适合当前任务、host 或 policy 的资产替代默认资产；
- warn：保留资产但提示 trust、permission、context cost 或 compatibility 风险。

产品对象关系是：

```text
Profile
  → baseline assets
  → Assembly Plan
  → resolve dependency closure and policy
  → Package Lock
  → Materialized Bundle
```

也可以不使用 Profile：

```text
Task + target host + constraints
  → Discovery
  → Assembly Plan
  → Package Lock
  → Materialized Bundle
```

概念边界：

| Concept | Nature | Lifecycle | Main Driver | Product Question |
|---|---|---|---|---|
| Profile | 持久化场景基线 | 长期存在 | Human user | What do I usually use for this scenario? |
| Assembly Plan | 任务级组合建议 | 一次任务或短期 | Agent / AAM | What should this agent use for this task right now? |
| Package Lock | 可复现解析结果 | 可审计快照 | AAM | What exact assets, versions, hashes, policies, and dependencies were approved? |
| Materialized Bundle | 目标宿主产物 | 被 host 消费 | AAM Adapter | What files/configs should be written for the target host? |

### 14.2 Profile Should Answer

一个 profile 应该回答：

- 这个场景通常要使用哪些 assets？
- 它面向哪个 target 或 target family？
- 它包含哪些依赖闭包？
- 它是否包含 unreviewed 或 risky assets？
- 它是否允许被外部 Agent 作为 base profile 使用？
- 导出后会生成哪些文件？
- 与上一次导出相比有什么变化？

### 14.3 Assembly Plan Should Answer

一个 Assembly Plan 应该回答：

- 当前任务是什么？
- 当前 target host 是什么？
- 是否基于某个 base Profile？
- 哪些 assets 来自 base Profile？
- 哪些 assets 是动态添加的？为什么？
- 哪些 assets 被排除？为什么？
- 哪些 assets 被 override？为什么？
- 依赖闭包是否完整？
- 是否存在 trust warning？
- 是否存在权限风险？
- 是否存在 host compatibility 问题？
- 预计上下文成本是多少？
- 为什么这个组合适合当前任务？

Assembly Plan 不是最终 lockfile，也不是直接安装动作。

它应该先被解释、审查，再进入 resolve / lock / materialize。

### 14.4 Package Lock Should Answer

Package Lock 不是 Package。Package 是源码/资产组织单元；Package Lock 是 approved Assembly Plan 或 Profile closure 经过依赖解析、版本固定、policy 检查和内容 hash 固定后的可复现使用快照。

它应该回答：

- 最终批准使用哪些 assets？
- 每个 asset 的版本、content hash 和来源是什么？
- 依赖闭包是什么？
- policy snapshot 是什么？
- 是否存在被接受的 warning？
- 该 lockfile 面向哪个 target host 或 host family？
- materialization 时应使用哪些 adapter 假设？

Package Lock 的产品意义是：

> 让一次 Agent 推荐或人工 Profile 导出变成可审计、可复现、可回滚的资产使用快照。

### 14.5 Rendering / Materialization Should Support

产品文案中可以继续使用 export，但核心模型应区分 rendering 与 materialization：

```text
Rendering:
  将 locked assets 转换成目标 host 的文件结构或配置结构。

Materialization:
  实际写入目标目录或生成 bundle artifact。
```

Rendering / materialization 流程应支持：

- preview；
- dry-run；
- dependency closure；
- target-specific rendering；
- export snapshot；
- export diff；
- warnings；
- reproducibility；
- trust policy enforcement；
- materialization approval；
- base Profile + Assembly Plan delta preview。

### 14.6 Target-specific Rendering

同一 Profile、Assembly Plan 或 Package Lock 未来可能渲染成：

- AGENTS.md；
- CLAUDE.md；
- Claude Code Skill；
- `.cursor/rules/*.mdc`；
- Codex-compatible instructions/config；
- OpenCode-compatible instructions/config；
- MCP config bundle；
- generic markdown bundle；
- generic JSON bundle。

产品语言中应把 export 视为 rendering / materialization，而不是简单复制。

---

## 15. Agent Gateway Product Requirements

Agent Gateway 是外部 AI Agent 接入 AAM 私有资产库的受控入口。

它的产品职责是：

- 让外部 Agent 能发现资产；
- 让外部 Agent 能读取安全的 Asset Card；
- 让外部 Agent 能请求 Assembly Plan；
- 让外部 Agent 能解释 selected / excluded assets；
- 让 AAM 能在过程中执行 trust、permission、visibility、dependency 和 host compatibility policy。

Agent Gateway 不应该让外部 Agent 默认拥有完整资产读取权、写入权或安装权。

### 15.1 MCP as Primary Dynamic Interface

AAM 应把 MCP Server 作为外部 AI Agent 的主要动态接口。

MCP Server 负责提供动态能力，例如：

```text
list_assets
search_assets
get_asset_card
get_asset_dependencies
propose_assembly_plan
explain_assembly_plan
validate_assembly_plan
```

早期 MCP 应默认是 read-only + propose-only。

高风险操作，例如 full content read、materialize、install、modify、delete，应默认禁用或需要显式确认。

### 15.2 Skill / AGENTS.md / Host Instruction Pack as Behavioral Guide

Skill 或 host instruction pack 不应该复制 registry 逻辑。

它们的职责是告诉外部 Agent：

- 什么时候应该调用 AAM；
- 为什么应该先读 Asset Card；
- 如何请求 Assembly Plan；
- 如何解释风险和排除理由；
- 为什么不能绕过 trust policy；
- 什么时候需要用户确认。

推荐交付形态：

```text
Claude Code:
  AAM Skill + MCP config example

Codex:
  AGENTS.md instruction pack + MCP config example
  optional Codex Agent Skill if the active host workflow supports skills

OpenCode:
  instructions/config pack

Generic MCP Client:
  README + server config template
```

产品原则：

> MCP 是动态能力接口；Skill / AGENTS.md / Host Instruction Pack 是行为引导层。

### 15.3 Agent Gateway Failure and Degraded Mode

外部 Agent 应把 AAM 视为受控能力提供者，而不是完成用户任务的唯一前提。

当 AAM MCP Server 未启动、无法连接、响应超时、workspace 未初始化、search 返回空、policy 阻断或某个 tool 调用失败时，外部 Agent 不应：

- 无限重试；
- 编造资产；
- 声称隐藏资产存在；
- 绕过 trust、visibility、permission 或 materialization policy；
- 因 AAM 不可用而完全阻塞一个原本可以继续推进的用户任务。

推荐原则：

> Fail closed for asset access. Fail soft for user task execution.

也就是说，资产访问失败时必须保守处理；但用户任务本身应尽可能降级为使用当前项目上下文继续执行。

产品和 host instruction pack 应支持以下降级策略：

| Failure Case | Expected Agent Behavior |
|---|---|
| MCP Server unavailable | 告知 AAM discovery 当前不可用；不要臆造资产；继续使用当前项目上下文。 |
| MCP timeout | 最多重试一次；仍失败则降级。 |
| Workspace not initialized | 提示用户初始化或连接 AAM workspace；当前任务可继续则继续。 |
| Search returns empty | 说明未找到匹配资产；不要声称没有任何资产，只说明本次搜索无匹配。 |
| Asset Card read denied | 不读取 full content；解释受限原因。 |
| Policy block | 解释 blocked reason；不使用该资产。 |
| Materialization disabled | 只输出 Assembly Plan 和解释，不写入目标 host 文件。 |

Skill / AGENTS.md / Host Instruction Pack 中应明确：

```text
If AAM tools fail or time out, do not keep retrying indefinitely.
Do not invent asset names or claim that unavailable assets exist.
Continue with the current repository context when possible.
Mention that AAM discovery was unavailable and proceed without AAM-provided assets.
```

---

## 16. Relationship Graph Product Requirements

图谱是长期差异化能力，但不能为了图谱而图谱。

图谱必须回答具体问题。

### 16.1 Priority Graph Views

优先级从高到低：

1. **Asset Ego Graph**  
   当前 asset 依赖什么、被谁依赖、被哪些 profile/lock 使用。

2. **Profile / Package Closure Graph**  
   某个 profile 或 package 最终包含哪些 assets 和 dependencies。

3. **Change Impact Graph**  
   修改某个 asset 会影响哪些 profile、exports、packages 和 host configs。

4. **Source Lineage Graph**  
   某个 asset/package 从哪个 local/GitHub source 导入，pin 到哪个 commit。

5. **Agent Assembly Graph**  
   某次 Assembly Plan 为什么选择这些 assets，它们之间的依赖和排除关系是什么。

6. **Diagnostic Graph**  
   高亮 orphan assets、broken references、cycles、risky imports。

7. **Global Graph**  
   用于整体探索，但不应成为默认高频视图。

### 16.2 Graph Design Principle

图谱默认应从一个问题出发，而不是默认展示所有节点。

正确方向：

```text
Show me impact
Show me closure
Show me lineage
Show me why this package was assembled
Show me orphan assets
```

错误方向：

```text
Draw everything in one huge graph
```

---

## 17. Governance Product Requirements

治理不是早期 MVP 的全部核心，但产品必须保留治理路径。

Agent-facing discovery 使治理更重要，因为资产不再只是人手动点击使用，而可能被外部 Agent 主动推荐。

### 17.1 Asset Lifecycle Status

建议状态：

```text
draft
active
deprecated
archived
```

### 17.2 Trust Status

建议状态：

```text
trusted
unreviewed
sandbox_only
blocked
needs_manual_review
```

### 17.3 Visibility and Access Levels

外部 Agent 访问资产信息应分层：

```text
Inventory Metadata:
  id, type, title, summary, tags, version, lifecycle, target compatibility.

Asset Card:
  intended use, dependencies, trust status, permission risk, quality status, context cost.

Content Preview:
  safe summary or partial preview.

Full Content / Materialization:
  only allowed by policy or explicit user approval.
```

### 17.4 Governance Questions

治理功能应帮助用户回答：

- 哪些 assets 长期未更新？
- 哪些 assets 没有被任何 profile/lock 使用？
- 哪些 assets 被大量复用，修改前需要谨慎？
- 哪些 imports 还未审查？
- 哪些 MCP/tool assets 可能有风险？
- 哪些 assets 有 eval coverage？
- 哪些 assets 应该 deprecated？
- 哪些 assets 被外部 Agent 频繁推荐但从未被用户采纳？
- 哪些 assets 因 trust warning 经常被排除？

治理不能阻塞个人快速迭代，但应该提供风险提示。

### 17.5 Rejection-to-Governance Loop

当用户因为 trust warning 取消 export / materialization，或拒绝外部 Agent 推荐的资产时，产品不应把拒绝视为终点。

拒绝应该成为治理入口。

典型场景包括：

- 用户拒绝 unreviewed asset 进入 profile；
- 用户取消包含 risky MCP/tool asset 的 Assembly Plan；
- 用户拒绝 Agent 推荐的某个资产；
- 用户因为 blocked / sandbox_only warning 取消 materialization；
- 用户多次忽略同一个推荐资产。

产品应引导用户选择明确下一步：

- Ignore once：仅本次忽略，不改变资产状态；
- Review now：进入资产审查页，查看来源、内容、依赖、权限和风险；
- Mark as trusted：审查后提升为 trusted；
- Mark as blocked：明确阻止未来推荐、组装和导出；
- Mark as sandbox_only：允许实验性使用，但不进入默认 profile/materialization；
- Deprecate asset：资产仍可追溯，但不再主动推荐；
- Suppress for this context：不改变全局状态，只在当前 project/profile/task type 下不再推荐。

MVP 最小闭环可以是：

```text
User rejects an unreviewed or risky asset
  → AAM records rejection reason
  → AAM offers Review now / Ignore once / Block asset
  → Future recommendations reduce repeated bad suggestions
```

这个微闭环的目标是避免 unreviewed assets 和 bad recommendations 长期僵尸化。

---

## 18. Product Principles

### 18.1 Inventory before Intelligence

先让用户知道自己有什么，再做智能推荐。

### 18.2 Search before Dashboard

搜索和浏览比漂亮 dashboard 更接近日常使用场景。

### 18.3 Asset Card before Full Content

外部 Agent 应优先读取安全摘要，而不是默认读取完整资产内容。

### 18.4 Assembly Plan before Materialization

外部 Agent 应先请求可解释的 Assembly Plan，再进入 resolve / lock / materialize。

### 18.5 Ego Graph before Global Graph

从单个 asset 的上下游关系开始，比一张全局大图更实用。

### 18.6 Trust before Automation

外部导入资产不能默认可信。自动识别、自动推荐、自动关系推断和 Agent-facing assembly 都必须可审查。

### 18.7 MCP before Host-specific Magic

动态资产发现和组装能力应优先通过 MCP 这类通用接口提供。Claude Code Skill、Codex AGENTS.md、OpenCode instructions 等 host-specific 交付物应作为引导层，而不是成为唯一事实源。

### 18.8 Export before Governance

用户需要先从复用中获得价值，再愿意投入治理。

### 18.9 Local-first before Team-first

先把个人工作流做顺，再扩展团队模式。

### 18.10 Explicit Metadata before Semantic Magic

早期优先依赖 manifest、tags、depends_on、source provenance、target_hosts、trust_status、lifecycle_status 和 permission metadata。Embedding 和语义推断是增强能力，不是事实来源。

### 18.11 Manifest as Source of Truth, Registry as Query Layer

Manifest、asset files、source provenance 和 run records 是持久事实来源。

Registry 是可重建的查询投影层，用于 CLI、API、UI、Agent Gateway、graph、assembly 和 materialization。

外部 Agent 的推荐、组装和解释都应以 Registry 中的事实投影为基础，而不是基于上下文中的猜测；但 Registry 不应变成唯一不可重建的事实源。

### 18.12 Fail Closed for Assets, Fail Soft for Tasks

当 Agent Gateway 不可用、超时或调用失败时，外部 Agent 不应绕过资产治理，也不应臆造资产。

资产访问应保守失败；用户任务应尽可能降级继续。

---

## 19. What AI Coding Agents Should Know

当 Claude Code / Codex / OpenCode 或其他 AI coding agents 执行本项目任务时，应始终记住：

1. 本项目不是 Agent runtime。
2. 本项目不是 pip/npm 风格包管理器。
3. 本项目不是公开市场。
4. 本项目是本地优先、私有优先的 Agent Asset Registry 与 Agent-facing Assembly Layer。
5. 第一用户价值是让分散资产变得可发现、可搜索、可复用。
6. Import → Inventory → Search/Browse → Profile/Package → Export 是人类用户核心产品闭环。
7. Task → Discover → Asset Card → Assembly Plan → Explain → Approve → Materialize 是外部 Agent 核心产品闭环。
8. Graph 是用来回答 impact、closure、lineage、diagnostics 和 assembly rationale，不是为了炫技。
9. 外部导入资产默认需要 provenance 和 trust state。
10. Export 是 target-specific rendering / materialization，不是简单复制文件。
11. UI 优先服务搜索、浏览、详情、依赖、来源、信任状态和推荐解释，而不是复杂设置页。
12. 在任何 UI 或交互流程中，都应让用户明确感知导入资产的信任状态。`unreviewed` 资产应有警告提示，`blocked` 资产应有禁用或阻断态；未审查或被阻断的资产不应静默进入 profile/materialization/lock。
13. 外部 Agent 不应默认读取完整资产内容；应先读取 Asset Card。
14. 外部 Agent 不应自己绕过 AAM 组装资产；应通过 Agent Gateway 请求 Assembly Plan。
15. Assembly Plan 可以从零生成，也可以基于已有 Profile 生成；Profile 是长期基线，Assembly Plan 是任务级动态建议。
16. MCP 是外部 Agent 的动态能力接口；Skill / AGENTS.md / Host Instruction Pack 是行为引导层。
17. 如果 AAM Gateway 不可用、超时或返回错误，外部 Agent 不应无限重试或臆造资产；应说明 AAM discovery 不可用，并在可能时降级为使用当前项目上下文继续任务。
18. 用户拒绝推荐或取消 materialization 后，产品应引导 Review now / Ignore once / Block asset 等治理动作。
19. 所有功能都应尊重 Manifest as source of truth、Registry as query layer、AAM as policy enforcer。

---

## 20. Product MVP Definition

产品 Core MVP 完成时，用户应该可以：

1. 创建一个 local workspace。
2. 从本地目录导入 Agent 资产。
3. 从 GitHub public repo/tag/commit 导入 Agent 资产。
4. 查看统一 asset inventory。
5. 搜索和过滤 assets。
6. 打开任意 asset detail，查看内容、metadata、source、hash、dependencies、reverse dependencies 和 trust status。
7. 查看任意 asset 的 Agent-readable Asset Card。
8. 创建或查看 Profile。
9. 预览 Profile closure。
10. 生成一个 task-specific Assembly Plan。
11. 基于已有 Profile 生成一个 task-specific Assembly Plan，并看到 add / remove / override delta。
12. 看到 selected assets、excluded assets、risks、warnings 和 rationale。
13. 看到 Package Lock 的可复现快照语义，包括 asset version、content hash、dependency closure 和 policy snapshot。
14. Render / materialize Profile closure 或 approved Assembly Plan 到至少一个真实 target host。
15. 配置至少一个外部 Agent 通过 MCP 调用 AAM 的 read-only / propose-only tools。
16. 当 Agent Gateway 不可用或超时时，外部 Agent 能按 host instruction pack 降级处理。
17. 在 profile/materialization/lock 中明确看到 unreviewed warning 和 blocked asset 阻断。
18. 在拒绝 risky / unreviewed recommendation 后，看到 Review now / Ignore once / Block asset 等下一步动作。
19. AAM 记录 rejection reason 和用户选择，供后续推荐和治理使用。
20. 通过基础 dependency / reverse dependency view 或 graph JSON 理解局部影响范围。

Core MVP 不强制要求完整 Dashboard 与 Relationship Graph UI。以下属于 MVP+：

1. 完整 dashboard 中的资产统计与健康面板；
2. asset ego graph、profile closure graph、source lineage graph 或 assembly graph 的可视化界面；
3. governance dashboard lite；
4. 复杂编辑、review form 和完整资产状态迁移。

如果 Core MVP 路径成立，产品就从“资产登记工具”变成了真正的：

> Agent Asset Workspace + Agent-facing Asset Assembly Control Plane.

如果 MVP+ 路径成立，产品会进一步形成 graph-aware、governance-aware 的长期差异化。

---

## 21. Non-MVP Product Ideas and Non-goals

以下想法有价值，但不应干扰 MVP：

- public marketplace；
- full Dashboard / Relationship Graph as a Core MVP prerequisite；
- full governance editing workflow as a Core MVP prerequisite；
- one-click install arbitrary third-party dependencies；
- executing agents directly；
- replacing Claude Code / Codex / OpenCode / Cursor；
- complex team RBAC；
- automated agent evaluation runtime；
- fully automatic asset rewriting；
- large-scale graph database；
- community rating；
- monetized asset store；
- real-time collaborative editing；
- automatic trust without review；
- external Agent unrestricted full-content access；
- external Agent unrestricted materialization or install rights；
- blocking all user work when Agent Gateway is unavailable。

这些可以作为远期方向或明确 non-goals，但不应进入早期产品闭环。

产品必须避免滑向三个方向：

1. 变成新的 Agent runtime。
2. 变成公开资产市场。
3. 变成外部 Agent 可以绕过本地信任治理的自动安装器。

---

## 22. Success Metrics

早期产品可以观察以下指标。

### 22.1 Activation Metrics

- 用户是否成功创建 workspace；
- 用户是否成功导入第一个 local package；
- 用户是否成功导入第一个 GitHub package；
- 用户是否看到 asset inventory；
- 用户是否打开 asset detail；
- 用户是否生成第一个 Asset Card；
- 用户是否生成第一个 profile；
- 用户是否生成第一个 Assembly Plan；
- 用户是否完成第一个 target rendering/export；
- 用户是否成功让一个外部 Agent 调用 AAM Gateway。

### 22.2 Utility Metrics

- asset search 次数；
- asset detail 访问次数；
- Asset Card 读取次数；
- profile 创建次数；
- Assembly Plan 生成次数；
- Assembly Plan 被采纳次数；
- Assembly Plan 被用户修改次数；
- base Profile → Assembly Plan delta 生成次数；
- Package Lock 生成次数；
- export dry-run 次数；
- export success 次数；
- dependency / reverse dependency view 使用次数；
- external Agent search_assets / propose_assembly_plan 调用次数。

### 22.3 Governance Metrics

- deprecated / archived asset 数量；
- unreviewed imports 数量；
- orphan assets 数量；
- stale assets 数量；
- duplicate candidates 数量；
- high-reuse assets 数量；
- blocked assets 数量；
- risky MCP/tool assets 数量；
- full-content access 被拒绝次数；
- materialization 被 policy 阻断次数；
- suppress-for-context 次数。

### 22.4 Trust Loop Metrics

信任闭环指标比单纯导入数量更能反映用户是否真正掌控资产库。

需要观察：

- 用户手动将 asset 从 `unreviewed` 标记为 `trusted` 的次数；
- 用户手动将 asset 从 `unreviewed` 标记为 `blocked` 的次数；
- 当前仍处于 `unreviewed` 状态的 assets 数量；
- trusted assets ratio；
- blocked imports ratio；
- profile/materialization/lock preview 中触发 unreviewed warning 的次数；
- 用户因 trust warning 取消 export 或 materialization 的次数；
- blocked asset 被阻止加入 profile/materialization/lock 的次数；
- 外部 Agent 推荐 unreviewed asset 后被用户拒绝的次数；
- 外部 Agent 推荐 trusted asset 后被用户采纳的次数；
- rejected recommendation count；
- rejection reason distribution；
- rejection → review conversion rate；
- rejection → blocked conversion rate；
- repeated rejected asset recommendation count。

这些指标衡量的不是“用户导入了多少资产”，而是：

> 用户是否真的审查、筛选并建立了可信资产库。

### 22.5 Agent Gateway Reliability Metrics

- MCP Server unavailable 次数；
- MCP timeout 次数；
- Agent Gateway tool error 次数；
- Agent degraded mode 触发次数；
- degraded mode 后用户任务继续完成次数；
- Agent 因 Gateway failure 无限重试或重复失败次数；
- Agent Gateway failure 后用户手动重试成功次数；
- empty search result 次数；
- policy block 被外部 Agent 正确解释次数。

### 22.6 Agent-facing Quality Signals

- 外部 Agent 是否能找到相关 assets；
- 外部 Agent 推荐的 assets 是否被用户采纳；
- Assembly Plan 是否减少用户手动复制 prompt/rule/config 的次数；
- Agent 是否能解释 selected / excluded assets；
- Agent 是否遵守 Asset Card before full content；
- Agent 是否遵守 Assembly Plan before materialization；
- Agent 是否避免使用 blocked assets；
- Agent 是否能在 context budget 内选择合适资产。

### 22.7 Product Quality Signals

- 用户是否减少重复创建类似 prompts/rules；
- 用户是否能更快找到已有资产；
- 用户是否愿意把新项目的 Agent instructions 迁入系统；
- 用户是否在修改 asset 前查看 impact；
- 用户是否持续维护 profiles；
- 用户是否愿意把 AAM 作为外部 AI Agent 的默认资产发现入口。

---

## 23. Product Summary

Agent Asset Management 的产品核心不是“管理文件”，而是管理用户长期积累的 Agent 能力资产。

它的第一价值是 inventory 和 discovery。

它的实用闭环是 profile composition、profile-based assembly、assembly plan、package lock / locked usage snapshot 和 target-specific materialization。

它的新核心差异是 Agent-facing Discovery and Assembly：外部 AI Agent 可以通过受控接口发现资产、读取 Asset Card、请求 Assembly Plan，并在用户或 policy 允许后使用 materialized bundle。

它的长期差异化是 source-aware、trust-aware、graph-aware、agent-consumable、failure-aware 的资产理解和治理能力。

产品必须避免三个陷阱：

1. 过早变成复杂平台，导致个人用户无法快速获得价值。
2. 过度追求图谱和智能推荐，忽略搜索、浏览、导入、导出这些日常高频路径。
3. 让外部 Agent 绕过资产库治理，直接读取、拼装或安装资产。

正确的产品路径是：

```text
Import scattered assets
  → Make them visible
  → Make them searchable
  → Make them understandable
  → Make them reusable by humans and external agents
  → Make rejection and failure actionable
  → Make them governable
```

这就是 Agent Asset Management 的产品价值闭环。
