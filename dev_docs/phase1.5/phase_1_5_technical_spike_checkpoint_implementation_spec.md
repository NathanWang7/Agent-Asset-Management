# Phase 1.5 Technical Spike Checkpoint Implementation Spec

## 1. 状态

Draft v0.4

本文档是 Agent Asset Management 项目的 **Phase 1.5 技术 Spike 检查点实施规格**。

本文档不是产品简报，也不是长期路线图，而是 Phase 1 完成后、Phase 2 开始前的阶段级工程执行文档。它的目标是把 Foundation & Roadmap Spec、Product Brief、Phase 1 Implementation Spec 和 Phase 1 实际实现结果转化为可以交给 Codex / Claude Code 执行的技术决策任务。

Phase 1.5 的主题是：

> Technical Spike Checkpoint

Phase 1.5 不是功能建设阶段，不应实现正式的 persistent registry、import service、HTTP API、MCP server、Web UI、Profile closure、Assembly Plan、Package Lock 或 materialization。它的职责是在进入这些阶段前，把关键技术选型、接口边界、文档路径和工程协作机制先冻结，避免 Phase 2 以后反复返工。

---

## 2. 权威文档路径

本项目当前采用以下文档布局。Phase 1.5 中所有新增开发文档、ADR、技术说明、review prompt 和阶段收尾材料都必须遵守该布局。

### 2.1 Overall 文档

```text
dev_docs/overall/agent_asset_management_foundation_spec_v0.4.1.md
dev_docs/overall/agent_asset_management_product_brief_v0.3.2.md
```

### 2.2 Phase 1 文档

```text
dev_docs/phase1/phase_1_core_package_system_mvp_implementation_spec.md
```

### 2.3 Phase 1.5 文档

```text
dev_docs/phase1.5/phase_1_5_technical_spike_checkpoint_implementation_spec.md
```

Phase 1.5 的 ADR、技术说明和阶段收尾材料也应放在：

```text
dev_docs/phase1.5/
```

除非某个文件明确是面向最终用户的使用文档，否则不要把 Phase 1.5 的开发文档放到 `docs/` 目录下。

### 2.4 Review Prompt 文档

```text
dev_docs/review/phase_1_5_claude_pr_review_prompt.md
dev_docs/review/phase_1_claude_pr_review_prompt.md
```

Phase 1.5 的 PR review 和 final closeout review 必须使用：

```text
dev_docs/review/phase_1_5_claude_pr_review_prompt.md
```

Phase 1 的旧 review prompt 仅作为历史参考，不应用于 Phase 1.5 PR。

### 2.5 用户文档

```text
docs/phase1_quickstart.md
```

`docs/` 目录用于用户可见的 quickstart、usage guide 和后续产品文档。Phase 1.5 的技术 spike、ADR、review report 和 closeout checklist 默认不属于用户文档，应放在 `dev_docs/phase1.5/` 或 `dev_docs/review/`。

---

## 3. 目标

Phase 1.5 的目标是基于 Phase 1 的实际实现，回答 Phase 2-7 会依赖的一组关键技术问题。

Phase 1.5 必须产出：

1. Phase 1 handoff audit。
2. registry storage 决策。
3. `InMemoryRegistry -> RegistryStore` 映射草案。
4. workspace registry boundary 决策。
5. UsageEvent / AuditLog / RejectionEvent 最小持久化占位决策。
6. API framework 决策。
7. MCP framework / SDK 决策。
8. Profile closure / Assembly Plan / profile_delta / Package Lock 的复杂度和接口边界说明。
9. Phase 3 minimal explain/validate 与 Phase 4A full explain/validate API 的切分决策。
10. frontend stack 决策。
11. graph visualization stack 决策。
12. CI workflow baseline。
13. GitHub issue / PR template。
14. phase release / tag convention。
15. Codex 与 Claude Code 的最终双审查报告。
16. Phase 1.5 closeout checklist。

Phase 1.5 的最重要产物不是可运行功能，而是让 Phase 2 可以直接开始 persistent registry、import service、query service 和 CLI usability 的实现，不再重新争论 storage、API、MCP、frontend、graph、CI 和 release 选择。

---

## 4. Scope

Phase 1.5 包含以下范围。

### 4.1 Phase 1 Handoff Audit

基于 Phase 1 implementation spec 和实际仓库状态，检查 Phase 1 是否已经足以支撑 Phase 2。

重点包括：

- `IndexedPackage` / `IndexedAsset` / `IndexedProfile` 是否包含 indexed timestamp。
- registry 是否包含 content hash、source provenance、trust status、lifecycle status、permission metadata、Asset Card projection 和 graph projection。
- CLI 是否通过 service boundary 使用 parser / validator / registry builder / query service。
- fixtures 是否满足 Phase 1 acceptance。
- tests、ruff、CLI smoke flow 是否通过。
- 是否存在已经误引入的 Phase 2+ 能力。

### 4.2 Registry Storage Decision

Phase 1.5 应对 SQLite / DuckDB / JSON 做出明确决策。

推荐默认决策：

```text
Primary registry store: SQLite
Debug/interchange export: deterministic JSON
Future analytics/reporting enhancement: DuckDB optional, not primary registry store
```

同时必须明确 workspace registry boundary。

推荐默认决策：

```text
One SQLite registry database per AAM workspace.
The SQLite file is workspace-scoped.
Do not design a multi-workspace shared registry database in Phase 2.
UsageEvent / AuditLog / RejectionEvent may keep workspace_id for future diagnostics and migration.
```

### 4.3 RegistryStore Mapping Draft

Phase 1.5 不实现 production RegistryStore，但必须写清楚 Phase 2 如何从 Phase 1 的 `InMemoryRegistry` 映射到持久化表。

草案映射：

```text
InMemoryRegistry.packages              -> registry_packages
InMemoryRegistry.assets                -> registry_assets
InMemoryRegistry.profiles              -> registry_profiles
InMemoryRegistry.asset_cards           -> registry_asset_cards
InMemoryRegistry.dependencies          -> registry_asset_dependencies
InMemoryRegistry.reverse_dependencies  -> derived query / view
InMemoryRegistry.graph.nodes           -> registry_graph_nodes
InMemoryRegistry.graph.edges           -> registry_graph_edges
InMemoryRegistry.validation_report     -> registry_validation_issues
```

### 4.4 Usage / Audit / Rejection Event Placeholder Decision

Phase 2 应预留 append-only 事件表或集合，但不实现推荐学习。

Phase 1.5 应定义最小占位形态：

```text
UsageEvent
AuditLog
RejectionEvent
```

它们应服务未来：

- Agent Gateway audit。
- rejection-to-governance loop。
- external agent recommendation tracking。
- degraded-mode diagnostics。
- materialization policy decision logging。

### 4.5 API Framework Decision

推荐默认决策：

```text
API framework: FastAPI
```

Phase 1.5 可以提供最小 pseudo-contract 或轻量 probe，但不实现 production Local Agent Gateway API。正式 API 属于 Phase 4A。

### 4.6 MCP Framework Decision

推荐默认决策：

```text
MCP framework: official MCP Python SDK
Transport priority: stdio first
```

Phase 1.5 可以验证 MCP tool schema / stdio server 的最低可行性，但不实现 production MCP Server。正式 MCP Server 属于 Phase 4B。

### 4.7 Profile / Assembly / Lockfile Complexity Note

Phase 1.5 应写清楚 Phase 3 的核心边界：

```text
ProfileClosureService
DiscoveryService
AssemblyPlanner
AssemblyPlanValidator
LockBuilder
MaterializationPreviewService
```

Phase 1.5 不实现这些 production service，只定义输入、输出、复杂度风险、依赖关系、scope 切分和 Phase 3 / Phase 4A 的边界。

### 4.8 Frontend and Graph Stack Decision

推荐默认决策：

```text
Frontend: React + Vite + TypeScript
Graph visualization: Cytoscape.js
React Flow: optional future explanatory/flow renderer only
```

Phase 1.5 不实现 Web UI 或 graph UI。正式 Web Asset Browser 属于 Phase 6；Dashboard & Relationship Graph MVP 属于 Phase 7。

### 4.9 CI / GitHub Workflow / Release Convention

Phase 1.5 应建立或检查：

- CI workflow。
- issue template。
- PR template。
- milestone / work order process。
- squash merge policy。
- phase tag convention。

推荐 tag：

```text
phase-1.5-technical-spike-checkpoint
```

tag 只能在 WO9 合并到 `main` 后、最终验证通过后创建。

### 4.10 Final Dual AI Review

Phase 1.5 的收尾必须包含两个独立审查：

1. Codex 根据 dev docs 对最终仓库状态进行全面审查。
2. Claude Code 根据 dev docs 对最终仓库状态进行全面审查。

只有两份最终审查报告都没有 unresolved P0/P1 findings，Phase 1.5 才能收尾并打 tag。

---

## 5. Non-goals

Phase 1.5 明确不做以下 production 能力：

1. 不实现 production persistent RegistryStore。
2. 不实现 migration system。
3. 不实现 local import workflow。
4. 不实现 GitHub importer。
5. 不实现 production HTTP API server。
6. 不实现 production MCP server。
7. 不实现 Web UI。
8. 不实现 graph visualization UI。
9. 不实现 profile closure execution。
10. 不实现 assembly planning。
11. 不实现 package lock generation。
12. 不实现 materialization。
13. 不实现 asset editing。
14. 不实现 semantic search。
15. 不实现 dashboard。
16. 不实现 team workspace。
17. 不实现 recommendation learning。
18. 不实现完整 governance workflow。

Phase 1.5 允许轻量 probe，但 probe 必须满足：

- 只在能实质降低技术不确定性时创建。
- 必须隔离在 `spikes/phase1.5/` 或等价 spike 目录下。
- 不成为 production code。
- 不引入 production runtime dependencies。
- 可以在后续阶段删除而不影响生产包。

---

## 6. Dependency Isolation Rules

Phase 1.5 的 spike dependency 必须隔离。

Python spike dependencies：

- 不得加入 production runtime dependencies。
- 如必须加入，应放在显式 optional / dev / spike dependency group。

Frontend / graph probes：

- 必须隔离在 spike 目录下。
- 不得提前创建 production frontend package，除非 ADR 明确批准该 repository structure。
- 不得让 React / Vite / Cytoscape 进入 production build path。

Phase 1.5 结束时，生产 Python package 应保持轻量。

---

## 7. Affected Modules and Paths

Phase 1.5 主要影响文档、CI 和轻量 spike 目录。

允许修改或新增：

```text
dev_docs/phase1.5/
dev_docs/review/phase_1_5_claude_pr_review_prompt.md
.github/workflows/
.github/pull_request_template.md
.github/ISSUE_TEMPLATE/
spikes/phase1.5/
```

可读取但不应随意修改：

```text
dev_docs/overall/agent_asset_management_foundation_spec_v0.4.1.md
dev_docs/overall/agent_asset_management_product_brief_v0.3.2.md
dev_docs/phase1/phase_1_core_package_system_mvp_implementation_spec.md
docs/phase1_quickstart.md
```

除非 WO 明确要求，不应修改：

```text
aam/
tests/
examples/
docs/
```

如果某个 spike 发现 Phase 1 代码存在阻塞 Phase 2 的结构性问题，应先记录为 P0/P1 finding，不要在 Phase 1.5 中顺手重构生产代码。

---

## 8. Work Orders

Phase 1.5 应拆成以下 9 个 Work Orders。每个 Work Order 应对应一个 GitHub issue、一个分支和一个 PR。

---

### WO1 — Phase 1 Handoff Audit

目标：确认 Phase 1 产物足以作为 Phase 2 输入。

交付物：

```text
dev_docs/phase1.5/phase_1_handoff_review.md
```

任务：

1. 根据 `dev_docs/phase1/phase_1_core_package_system_mvp_implementation_spec.md` 审查 Phase 1 实现。
2. 检查 indexed timestamp。
3. 检查 registry 是否包含 content hash、Asset Card projection、dependencies、reverse dependencies、source provenance、trust、lifecycle、permissions 和 graph projection。
4. 检查 CLI 是否通过 service boundary。
5. 检查 required fixtures。
6. 运行本地测试、ruff 和 CLI smoke flow。
7. 输出 handoff review。

验收标准：

- handoff review 明确列出 pass / gap / risk。
- 如有 gap，按 P0/P1/P2/P3 分类。
- 不修改 production code，除非只是极小文档或路径修正。

---

### WO2 — Registry Storage Spike and ADR

目标：冻结 Phase 2 的 registry persistence 方向。

交付物：

```text
dev_docs/phase1.5/adr_0001_registry_storage.md
dev_docs/phase1.5/registry_schema_draft.md
spikes/phase1.5/sqlite_registry_probe.py       # only if materially useful
```

任务：

1. 比较 SQLite / DuckDB / JSON。
2. 决策 primary registry store。
3. 明确 one SQLite DB per workspace 的边界。
4. 写出 `InMemoryRegistry -> RegistryStore` 映射。
5. 如有必要，写最小 SQLite probe。
6. 说明 DuckDB 后续作为 analytics option 的位置。

验收标准：

- ADR 有明确 decision / context / alternatives / rationale / consequences。
- registry schema draft 足以支撑 Phase 2 implementation spec。
- 明确不实现 production RegistryStore。
- spike dependency 不进入 production runtime dependencies。

---

### WO3 — Usage / Audit / Rejection Event Placeholder ADR

目标：冻结 Phase 2 的事件占位边界。

交付物：

```text
dev_docs/phase1.5/adr_0002_usage_audit_rejection_events.md
```

任务：

1. 定义 UsageEvent 最小字段。
2. 定义 AuditLog 最小字段。
3. 定义 RejectionEvent 最小字段。
4. 明确 append-only 原则。
5. 明确 Phase 2 只做 placeholder，不做 recommendation learning。
6. 对齐未来 rejection-to-governance loop。

验收标准：

- 事件模型能支撑 Agent Gateway audit、rejection reason、future recommendation signals。
- 不引入复杂治理工作流。
- 不实现事件写入生产代码。

---

### WO4 — API and MCP Framework Spike

目标：冻结 Phase 4A / 4B 的 API 与 MCP 技术栈方向。

交付物：

```text
dev_docs/phase1.5/adr_0003_api_and_mcp_framework.md
spikes/phase1.5/fastapi_probe/                 # only if materially useful
spikes/phase1.5/mcp_probe/                     # only if materially useful
```

任务：

1. 比较 FastAPI / Litestar / other。
2. 决策 FastAPI 是否作为默认 Local Agent Gateway API framework。
3. 比较 MCP Python SDK 和替代方案。
4. 决策 official MCP Python SDK + stdio first。
5. 如有必要，做最小 probe。
6. 写出 Phase 4A / 4B 的边界。

验收标准：

- ADR 明确 API 和 MCP 的关系。
- 明确 MCP 不实现 registry / assembly business logic。
- 明确 production API 属于 Phase 4A，production MCP server 属于 Phase 4B。
- probe code 可删除，不影响 production package。

---

### WO5 — Profile / Assembly / Lockfile Complexity Note

目标：冻结 Phase 3 的组合、组装和锁定边界。

交付物：

```text
dev_docs/phase1.5/profile_assembly_lock_complexity_note.md
dev_docs/phase1.5/adr_0004_composition_assembly_lock_boundary.md
```

任务：

1. 定义 ProfileClosureService 输入/输出。
2. 定义 DiscoveryService 输入/输出。
3. 定义 AssemblyPlanner 输入/输出。
4. 定义 AssemblyPlanValidator 边界。
5. 定义 LockBuilder 边界。
6. 定义 MaterializationPreviewService 边界。
7. 说明 dependency closure、profile_delta、warnings、reason codes、policy snapshot 的复杂度。
8. 决定 Phase 3 minimal explain/validate 与 Phase 4A full explain/validate API 的切分。

验收标准：

- 不实现 production profile closure / assembly / lockfile。
- Note 足以支持 Phase 3 implementation spec。
- Package、Profile、Assembly Plan、Package Lock、Materialization 的概念边界清晰。

---

### WO6 — Frontend and Graph Stack ADR

目标：冻结 Phase 6 / 7 的前端与图谱可视化技术方向。

交付物：

```text
dev_docs/phase1.5/adr_0005_frontend_and_graph_stack.md
spikes/phase1.5/react_vite_probe/              # only if materially useful
spikes/phase1.5/cytoscape_probe/               # only if materially useful
```

任务：

1. 比较 React + Vite / Next.js / other。
2. 决策 React + Vite + TypeScript。
3. 比较 Cytoscape.js / React Flow / Sigma.js / G6。
4. 决策 Cytoscape.js 作为主 relationship graph renderer。
5. 说明 React Flow 只作为未来 explanatory / flow renderer 的备选。
6. 如有必要，做最小 isolated probe。

验收标准：

- ADR 不提前创建 production Web UI。
- frontend / graph probe 不污染 production build。
- 明确 Phase 6 和 Phase 7 的边界。

---

### WO7 — CI, GitHub Templates, and Release Convention

目标：稳定 Phase 2+ 的 PR-driven AI coding workflow。

交付物：

```text
.github/workflows/ci.yml
.github/pull_request_template.md
.github/ISSUE_TEMPLATE/work_order.md
dev_docs/phase1.5/adr_0006_ci_and_release_convention.md
```

任务：

1. 检查或创建 CI baseline。
2. 检查或创建 PR template。
3. 检查或创建 issue template。
4. 明确 work order issue 的字段。
5. 明确 squash merge policy。
6. 明确 phase tag convention。
7. 明确 WO9 后才允许打 Phase 1.5 tag。

验收标准：

- CI 可以运行 pytest、ruff check（如已配置）、CLI help smoke。
- templates 能支撑 AI-assisted PR review。
- release/tag convention 无歧义。

---

### WO8 — Final Phase 1.5 Technical Spike Note

目标：汇总 Phase 1.5 的所有决策，为 Phase 2 implementation spec 提供入口。

交付物：

```text
dev_docs/phase1.5/phase_1_5_technical_spike_note.md
```

任务：

1. 汇总 WO1-WO7 的决策。
2. 列出 accepted decisions。
3. 列出 deferred decisions。
4. 列出 Phase 2 必须遵守的 technical constraints。
5. 列出 Phase 2 implementation spec 的建议结构。
6. 列出 unresolved P2/P3 items。

验收标准：

- Phase 2 可以直接基于此 note 开写 implementation spec。
- 不引入新决策而不引用对应 ADR。
- 不把 Phase 1.5 描述成已实现生产功能。

---

### WO9 — Final Dual AI Review and Phase Closeout

目标：通过 Codex 和 Claude Code 的双重最终审查后，才允许 Phase 1.5 收尾。

交付物：

```text
dev_docs/review/phase_1_5_codex_final_review.md
dev_docs/review/phase_1_5_claude_final_review.md
dev_docs/phase1.5/phase_1_5_closeout_checklist.md
```

任务：

1. Codex 基于 dev docs 对最终仓库状态进行独立全面审查。
2. Claude Code 基于 `dev_docs/review/phase_1_5_claude_pr_review_prompt.md` 对最终仓库状态进行独立全面审查。
3. 两份审查都必须按 P0/P1/P2/P3 分类。
4. 如果存在 P0/P1，必须修复后重新审查。
5. 完成 closeout checklist。
6. WO9 PR 不创建、不推送 phase tag。
7. WO9 squash merge 到 main 后，再 final verification；通过后才创建 tag。

验收标准：

- Codex final review 无 unresolved P0/P1。
- Claude final review 无 unresolved P0/P1。
- closeout checklist 完整准确。
- Phase 1.5 没有引入 production Phase 2+ 能力。
- main 上 final verification 通过。
- tag 只在 WO9 合并后创建。

---

## 9. Acceptance Criteria

Phase 1.5 完成时必须满足：

1. `dev_docs/phase1.5/phase_1_5_technical_spike_checkpoint_implementation_spec.md` 存在且为当前执行 spec。
2. WO1-WO9 均有 GitHub issue、PR 和 squash merge 记录。
3. Phase 1 handoff audit 完成。
4. registry storage ADR 完成。
5. workspace registry boundary 决策完成。
6. registry schema draft 完成。
7. UsageEvent / AuditLog / RejectionEvent ADR 完成。
8. API / MCP ADR 完成。
9. Profile / Assembly / Lockfile complexity note 完成。
10. Frontend / Graph stack ADR 完成。
11. CI / GitHub template / release convention ADR 完成。
12. Final technical spike note 完成。
13. Codex final review 完成且无 unresolved P0/P1。
14. Claude final review 完成且无 unresolved P0/P1。
15. closeout checklist 完成。
16. Phase 1.5 没有实现 production Phase 2+ capability。
17. Spike dependencies 均隔离。
18. main 分支 final verification 通过。
19. tag `phase-1.5-technical-spike-checkpoint` 指向 WO9 合并后的 main commit。

---

## 10. Testing and Verification Plan

每个 Work Order PR 至少运行：

```bash
pytest
ruff check .   # if configured
aam --help    # or equivalent CLI help command, if CLI exists
```

Docs-only PR 仍应运行基础测试，除非仓库当前没有可运行测试；若无法运行，应在 PR 中说明原因。

Spike PR 额外要求：

- probe 有最小 smoke command 或 README。
- probe 可以删除而不影响 production package。
- probe dependency 不进入 production runtime dependencies。

WO9 final verification 应运行：

```bash
git checkout main
git pull --ff-only
pytest
ruff check .   # if configured
aam --help    # or equivalent CLI help command
```

并检查：

```bash
gh pr checks <WO9_PR_NUMBER>
git status --short
```

---

## 11. Risks and Mitigations

### Risk 1 — Spike 变成 Production Implementation

问题：Codex 可能把 Phase 1.5 做成 Phase 2 实现。

缓解：所有 Work Order 明确 non-goals；review prompt 必须检查 Phase 2+ capability 越界。

### Risk 2 — 文档路径混乱

问题：Phase 1.5 技术文档被写入 `docs/`，导致用户文档与开发文档混杂。

缓解：Phase 1.5 所有开发文档、ADR、review report 默认写入 `dev_docs/phase1.5/` 或 `dev_docs/review/`。

### Risk 3 — Spike Dependency 污染 Production Package

问题：FastAPI、MCP、React、Vite、Cytoscape 等被加入 production dependency。

缓解：所有 spike dependency 必须 optional/dev/spike-only；frontend probe 必须隔离。

### Risk 4 — Registry Storage 决策没有 Workspace Boundary

问题：Phase 2 开始时不清楚是一个 workspace 一个 DB，还是共享 DB 多 workspace。

缓解：WO2 必须明确 one SQLite DB per workspace 的默认边界。

### Risk 5 — Final Review 变成形式化总结

问题：WO9 的 Codex / Claude review 只是总结工作，而不是审查最终状态。

缓解：两份 final review 都必须是独立 review pass，必须基于 dev docs 与最终仓库状态，必须按 P0/P1/P2/P3 分类。

### Risk 6 — Tag 指向错误 Commit

问题：在 WO9 分支上提前打 tag。

缓解：WO9 PR 不打 tag；必须在 WO9 squash merge 后同步 main，再 final verification，通过后才打 tag。

---

## 12. Review Checklist

每个 Phase 1.5 PR review 时应确认：

- [ ] PR 是否只完成当前 Work Order。
- [ ] 是否没有实现 production Phase 2+ capability。
- [ ] 是否遵守 `dev_docs/` 与 `docs/` 的目录边界。
- [ ] 是否使用正确的 authoritative docs。
- [ ] 是否保持 Manifest as source of truth。
- [ ] 是否保持 Registry as query projection。
- [ ] 是否没有重新定义 Phase 1 core models。
- [ ] 是否没有污染 production dependencies。
- [ ] ADR 是否有 decision / context / alternatives / rationale / consequences。
- [ ] probe 是否确实降低不确定性，且可删除。
- [ ] 测试或验证是否足够。
- [ ] P0/P1 findings 是否已解决。

WO9 额外确认：

- [ ] Codex final review 已完成。
- [ ] Claude final review 已完成。
- [ ] 两份 review 均无 unresolved P0/P1。
- [ ] closeout checklist 完整。
- [ ] final verification 在 main 上运行。
- [ ] phase tag 在 WO9 合并后创建。

---

## 13. Phase 1.5 Completion Definition

Phase 1.5 可以视为完成，当且仅当：

1. WO1-WO9 全部完成并 squash merge。
2. 所有 acceptance criteria 通过。
3. 所有 P0/P1 findings 均已解决。
4. Codex final review 和 Claude final review 均无 unresolved P0/P1。
5. `dev_docs/phase1.5/phase_1_5_technical_spike_note.md` 完成。
6. `dev_docs/phase1.5/phase_1_5_closeout_checklist.md` 完成。
7. main 上 final verification 通过。
8. tag `phase-1.5-technical-spike-checkpoint` 已创建并指向最终 main commit。
9. Phase 2 implementation spec 可以直接开写。

---

## 14. Handoff to Phase 2

Phase 1.5 完成后，Phase 2 应进入：

> Persistent Registry, Import Service & CLI Usability

Phase 2 implementation spec 应直接消费 Phase 1.5 的以下产物：

```text
dev_docs/phase1.5/phase_1_handoff_review.md
dev_docs/phase1.5/adr_0001_registry_storage.md
dev_docs/phase1.5/registry_schema_draft.md
dev_docs/phase1.5/adr_0002_usage_audit_rejection_events.md
dev_docs/phase1.5/phase_1_5_technical_spike_note.md
```

Phase 2 不应重新争论 registry storage、workspace registry boundary、event placeholder、基础 CI/release convention 等 Phase 1.5 已决事项。
