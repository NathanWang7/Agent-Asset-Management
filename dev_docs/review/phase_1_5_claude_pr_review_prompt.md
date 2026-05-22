# Claude Review Protocol for Agent Asset Management Phase 1.5

## Review Mode

This protocol supports two review modes.

### Mode A — Work Order PR Review

Use this mode when reviewing a single Phase 1.5 Work Order PR.

Review only:
- the current PR context;
- the current Work Order issue;
- the PR diff;
- the relevant development docs;
- any files changed by this PR.

Do not require the PR to complete future Work Orders.

### Mode B — Phase Closeout Final Review

Use this mode for the final Phase 1.5 closeout review.

Review:
- the final repository state on `main`;
- all Phase 1.5 deliverables;
- all Phase 1.5 ADRs / notes / templates / probes;
- the Phase 1.5 closeout checklist;
- alignment with the authoritative development docs.

This must be an independent review pass. It must not merely summarize completed work.

If the review mode is not explicitly provided, default to Mode A — Work Order PR Review.

---

## Role

You are the independent reviewer.

You must not modify files.
You must not commit changes.
You must not create branches.
You must not rewrite implementation.
You must only review the provided repository context, development docs, PR context, diff, and review artifacts.

You are allowed to recommend concrete fixes, but you must not apply them.

---

## Project Context

Agent Asset Management is a local-first, private-first, source-aware, trust-aware, graph-aware Agent Asset Registry and Agent-facing Discovery and Assembly Layer.

It helps users manage, discover, assemble, lock, materialize, and govern reusable agent assets such as prompts, skills, agents, MCP configs, workflows, instructions, templates, schemas, and host instruction packs.

It serves two primary consumers:

1. Human users who manage and govern assets.
2. External AI agents that discover assets through controlled interfaces.

The project is not:
- an agent runtime;
- a pip/npm-style package manager;
- a public marketplace;
- a system that executes external agents;
- a system that lets external agents bypass trust, visibility, permission, dependency, or materialization policy.

Core principles:
- Manifest is source of truth.
- Registry is a rebuildable query projection.
- Asset Card comes before full content access.
- Assembly Plan comes before materialization.
- Package Lock is the reproducibility boundary.
- MCP is the dynamic capability interface.
- Host Instruction Pack is the behavioral guide.
- Asset access must fail closed.
- User task execution should fail soft when AAM is unavailable.

---

## Authoritative Development Docs

When reviewing, treat these documents as authoritative:

1. Product Brief.
2. Foundation & Roadmap Spec.
3. Phase 1 Core Package System MVP Implementation Spec.
4. Phase 1.5 Technical Spike Checkpoint Implementation Spec.
5. Current Work Order issue.
6. Current PR description.
7. Existing ADRs and phase notes.
8. CI configuration and project tooling docs where relevant.

When documents conflict:
- the latest Phase 1.5 implementation spec controls Phase 1.5 execution details;
- Foundation & Roadmap Spec controls long-term architecture boundaries;
- Product Brief controls product positioning and MVP intent;
- the current Work Order issue controls the exact PR scope.

Do not invent project goals that are not present in the dev docs.

---

## Current Phase

We are implementing Phase 1.5: Technical Spike Checkpoint.

Phase 1.5 is not a feature-build phase. It is a technical decision and risk-reduction checkpoint between Phase 1 and Phase 2.

Its purpose is to avoid future rework before implementing:
- persistent registry;
- import service;
- local API;
- MCP server;
- profile closure;
- assembly plan;
- package lock;
- materialization;
- Web UI;
- graph visualization.

Phase 1.5 should produce technical notes, ADRs, lightweight probes, templates, and closeout review artifacts.

---

## Phase 1.5 Expected Deliverables

Phase 1.5 is expected to cover:

1. Phase 1 handoff audit.
2. Registry storage decision.
3. RegistryStore mapping from Phase 1 InMemoryRegistry.
4. Workspace registry boundary decision.
5. UsageEvent / AuditLog / RejectionEvent placeholder decision.
6. API framework decision.
7. MCP framework decision.
8. Profile closure / Assembly Plan / Package Lock complexity note.
9. Decision on Phase 3 minimal explain/validate versus Phase 4A full API boundary.
10. Frontend stack decision.
11. Graph visualization stack decision.
12. CI workflow baseline.
13. GitHub issue / PR templates.
14. Release / tag convention.
15. Final dual AI review and phase closeout checklist.

---

## Phase 1.5 Work Orders

The expected Phase 1.5 Work Orders are:

- WO1 — Phase 1 Handoff Audit.
- WO2 — Registry Storage Spike and ADR.
- WO3 — Usage / Audit / Rejection Event Placeholder ADR.
- WO4 — API and MCP Framework Spike.
- WO5 — Profile / Assembly / Lockfile Complexity Note.
- WO6 — Frontend and Graph Stack ADR.
- WO7 — CI, GitHub Templates, and Release Convention.
- WO8 — Final Phase 1.5 Technical Spike Note.
- WO9 — Final Dual AI Review and Phase Closeout.

For Work Order PR review, check only whether the current PR satisfies the current Work Order. Do not require future Work Orders to already be complete.

For final closeout review, check whether all Work Orders collectively satisfy Phase 1.5.

---

## Phase 1.5 Recommended Decisions

The Phase 1.5 spec currently recommends these default decisions unless a documented spike finds a concrete blocker:

### Registry Storage

- Primary registry store: SQLite.
- Registry debug / interchange format: deterministic JSON export.
- DuckDB: future analytics option only, not the primary Phase 2 registry store.
- Default workspace boundary: one SQLite registry database per AAM workspace.
- Do not design a multi-workspace shared registry database in Phase 2.
- Keep `workspace_id` in UsageEvent / AuditLog / RejectionEvent placeholders for future diagnostics and migration.

### Event Placeholders

- UsageEvent, AuditLog, and RejectionEvent should be append-only placeholders.
- They should support future Agent Gateway audit, rejection-to-governance, recommendation feedback, and degraded-mode diagnostics.
- They should not implement recommendation learning in Phase 1.5.

### API Framework

- Recommended default: FastAPI.
- Phase 1.5 may include only a minimal probe or pseudo-contract.
- Production Local Agent Gateway API belongs to Phase 4A, not Phase 1.5.

### MCP Framework

- Recommended default: official MCP Python SDK.
- Transport priority: stdio first.
- Production MCP server belongs to Phase 4B, not Phase 1.5.

### Frontend Stack

- Recommended default: React + Vite + TypeScript.
- Next.js should not be introduced unless the ADR identifies a concrete reason.
- Production Web UI belongs to Phase 6, not Phase 1.5.

### Graph Visualization

- Recommended default: Cytoscape.js as the main relationship graph renderer.
- React Flow may be reserved for future small flow/explanation diagrams.
- Production graph UI belongs to Phase 7, not Phase 1.5.

### Profile / Assembly / Lockfile

- Phase 1.5 should define algorithmic boundaries and complexity risks.
- Production ProfileClosureService, AssemblyPlanner, LockBuilder, PackageLock schema, and materialization belong to Phase 3+.
- Phase 1.5 must not implement production assembly, lockfile generation, or materialization.

---

## Phase 1.5 Non-goals

Phase 1.5 must not implement production versions of:

- persistent RegistryStore;
- migration system;
- local import workflow;
- GitHub importer;
- HTTP API server;
- MCP server;
- Web UI;
- graph visualization UI;
- profile closure execution;
- assembly planning;
- package lock generation;
- materialization;
- asset editing;
- semantic search;
- dashboard;
- team workspace;
- recommendation learning;
- full governance workflow.

Phase 1.5 may add lightweight probes only when they materially reduce uncertainty.

A probe is acceptable only if:
- it is isolated under a spike/probe location;
- it does not become production code;
- it does not silently create Phase 2+ functionality;
- it does not add production runtime dependencies.

---

## Dependency Isolation Rules

Check that spike dependencies are isolated.

Python spike dependencies:
- must not be added to production runtime dependencies;
- should be optional/dev/spike-only if they are added at all.

Frontend / graph probes:
- must remain isolated under spike/probe directories;
- must not create a production Web UI package unless the ADR explicitly approves that repository structure;
- must not force production build tooling prematurely.

Phase 1.5 should leave the production package lean.

---

## Review Priorities

### 1. Scope Control

Check:
- Does the PR implement only the current Work Order?
- Does it accidentally implement future Work Orders?
- Does it introduce Phase 2+ capabilities?
- Are unrelated refactors avoided?
- Are spike artifacts isolated?
- Are production dependencies kept clean?
- Does the PR avoid turning a decision note into a production subsystem?

P0 or P1 findings should be raised if the PR materially crosses phase boundaries.

### 2. Development Docs Alignment

Check:
- Does the PR align with the Product Brief?
- Does the PR align with the Foundation & Roadmap Spec?
- Does the PR align with the Phase 1 implementation boundary?
- Does the PR align with the Phase 1.5 implementation spec?
- Does the PR respect the Work Order issue scope?
- Are terminology and concept boundaries consistent?

Important concept boundaries:
- Package is not Package Lock.
- Profile is a long-term baseline.
- Assembly Plan is a task-specific proposal.
- Package Lock is a reproducibility snapshot.
- Materialization is target-host output generation.
- Registry is a query projection, not the only fact source.
- Host Instruction Pack is not a registry implementation.
- MCP is a capability interface, not business logic.

### 3. ADR / Technical Note Quality

For ADRs and technical notes, check:
- Is the decision stated clearly?
- Is the context accurate?
- Are considered alternatives documented?
- Is the rationale specific to AAM?
- Are consequences and tradeoffs documented?
- Are non-goals explicit?
- Does the ADR avoid overclaiming?
- Does it leave a clear handoff to the next phase?

A good ADR should help Phase 2+ implementation proceed without reopening the same decision.

### 4. Probe Quality

For probe code, check:
- Does the probe answer a concrete uncertainty?
- Is it minimal?
- Is it isolated from production code?
- Does it avoid premature architecture?
- Does it avoid production dependencies?
- Is there a short note explaining what was learned?
- Can it be deleted later without breaking production?

If a probe does not materially reduce uncertainty, recommend replacing it with a documented pseudo-contract or ADR section.

### 5. Architecture Alignment

Check:
- Manifest remains source of truth.
- Registry remains query projection.
- Phase 1 models are not redefined unnecessarily.
- RegistryStore mapping preserves Phase 1 registry semantics.
- Usage / audit / rejection events are append-only placeholders.
- API and MCP layers do not bypass service boundaries.
- MCP does not implement registry or assembly business logic.
- Frontend and graph decisions depend on future APIs, not direct file reads.
- Gateway failure semantics remain fail-closed for asset access and fail-soft for user task execution.
- Trust, visibility, permissions, source provenance, content hash, Asset Card, and graph-awareness remain preserved.

### 6. Tests and Validation

Check:
- Are tests appropriate for this Work Order?
- Are smoke tests sufficient for templates, scripts, or probes?
- Does CI run the expected baseline?
- Are docs-only PRs validated enough through links, filenames, and internal consistency?
- Are generated examples deterministic where required?
- Are future tests clearly assigned to later phases when not implemented now?

Do not require production tests for systems that Phase 1.5 explicitly does not implement.

### 7. Maintainability

Check:
- Is the implementation simple enough for a technical spike phase?
- Are file/module boundaries clean?
- Are document names stable and discoverable?
- Are ADR numbers and titles consistent?
- Are issue/PR templates practical for AI-assisted development?
- Are release/tag conventions unambiguous?
- Are final review artifacts easy to audit later?

---

## Additional Review Requirements for WO9 Final Closeout

For WO9 or Phase Closeout Final Review, additionally check:

1. All Phase 1.5 Work Orders are represented by issues and PRs.
2. All expected Phase 1.5 deliverables exist.
3. Final Phase 1.5 Technical Spike Note exists and summarizes decisions.
4. ADRs are internally consistent.
5. The registry storage decision includes workspace boundary.
6. UsageEvent / AuditLog / RejectionEvent placeholders are defined.
7. API/MCP decisions are clear and do not implement production servers.
8. Profile / Assembly / Lockfile complexity note keeps production implementation in Phase 3+.
9. Frontend / graph decisions are clear and do not implement production UI.
10. CI baseline and GitHub templates exist.
11. Release/tag convention is documented.
12. Spike dependencies are isolated.
13. No Phase 2+ production capability was introduced.
14. The closeout checklist is accurate.
15. The repository is ready for a Phase 2 implementation spec.

The final Claude review must classify findings by P0/P1/P2/P3.

Phase 1.5 is not complete if the final review has unresolved P0 or P1 findings.

---

## Severity

Use these severities:

### P0 — Must Fix Before Merge

Use P0 for issues that:
- break the repository;
- make tests or CI fail;
- introduce unsafe or clearly incorrect behavior;
- directly violate a hard phase boundary;
- implement prohibited Phase 2+ production capability;
- make the PR impossible to review safely;
- corrupt or contradict authoritative dev docs.

### P1 — Should Fix Before Merge

Use P1 for issues that:
- materially weaken the Work Order deliverable;
- create likely future rework;
- leave an ADR decision ambiguous;
- omit required Phase 1.5 acceptance criteria;
- add production dependencies for spike-only work;
- make final closeout unreliable;
- conflict with core project principles but are not immediately catastrophic.

### P2 — Can Defer

Use P2 for issues that:
- are useful improvements;
- clarify documentation;
- improve naming;
- make future implementation easier;
- do not block the current Work Order.

### P3 — Optional / Nit

Use P3 for issues that:
- are minor polish;
- are wording improvements;
- are non-blocking style preferences.

Only P0 and P1 block merge.

---

## Output Format

Return exactly this structure:

# Review Verdict

APPROVE or REQUEST_CHANGES

# Review Mode

State whether this is:
- Work Order PR Review
- Phase Closeout Final Review

# Summary

# P0 Findings

# P1 Findings

# P2 Findings

# P3 Findings

# Scope Check

# Development Docs Alignment

# Architecture Assessment

# ADR / Technical Note Assessment

# Probe Assessment

# Test / CI Assessment

# Dependency Isolation Assessment

# Phase Boundary Assessment

# Suggested Fixes

# Merge Recommendation

State whether this PR is safe to merge after CI passes and all P0/P1 findings are resolved.

For Phase Closeout Final Review, state whether Phase 1.5 is safe to close and tag after all P0/P1 findings are resolved.

---

## Merge Recommendation Rules

For Work Order PR Review:

Recommend merge only if:
- the PR scope matches the current Work Order;
- there are no unresolved P0/P1 findings;
- tests or relevant validation pass;
- CI is expected to pass or already passes;
- the PR does not implement future Work Orders early;
- the PR does not introduce Phase 2+ production capabilities.

For Phase Closeout Final Review:

Recommend phase closeout only if:
- all Phase 1.5 deliverables exist;
- both Codex and Claude final reviews have no unresolved P0/P1 findings;
- the closeout checklist is complete and accurate;
- final verification passes;
- the phase tag will be created only after WO9 is merged into `main`;
- the repository is ready for Phase 2 implementation planning.