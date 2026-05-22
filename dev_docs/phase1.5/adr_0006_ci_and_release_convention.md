# ADR 0006: CI and Release Convention

## Status

Accepted (Phase 1.5), 2026-05-22.

## Decision

Use GitHub Actions as the baseline CI runner for pull requests and pushes to `main`.

Phase 1.5 CI should run:

- package install with development dependencies;
- `ruff check .`;
- `pytest`;
- installed CLI help smoke through `aam --help`.

Use GitHub Work Order issues and pull request templates for phase execution. Every Work Order issue must include Goal, Scope, Deliverables, Acceptance Criteria, Non-goals, Test commands, and an explicit warning not to implement production Phase 2+ capabilities unless currently scoped.

Use squash merge only for Work Order PRs. Do not use merge commits. Delete the branch after squash merge.

Use phase tags only after all Work Orders for the phase are merged into `main` and final verification passes.

The Phase 1.5 tag is:

```text
phase-1.5-technical-spike-checkpoint
```

This tag must not be created or pushed from the WO9 branch. It can only be created after WO9 is squash-merged into `main`, `main` is fast-forward synced, final verification passes, final review reports show no unresolved P0/P1 findings, the closeout checklist exists, and the working tree is clean.

## Context

Phase 1.5 is a technical spike checkpoint with many small documentation and process Work Orders. The risk is not production code complexity; the risk is scope drift, skipped review gates, inconsistent issue/PR bodies, or premature phase tagging.

The repository already has a Python package with `pytest`, optional/dev `ruff`, and an installed CLI entry point `aam`. Phase 1.5 should make those checks explicit in CI and in PR templates.

## Work Order Issue Requirements

Each Work Order issue must include:

- Goal;
- Scope;
- Deliverables;
- Acceptance Criteria;
- Non-goals;
- Test commands;
- explicit warning not to implement production Phase 2+ capabilities.

For Phase 1.5, labels should include:

- `phase-1.5`;
- `work-order`;
- `docs`;
- plus specific labels such as `adr`, `spike`, `ci`, or `review`.

The issue should be assigned to the current phase milestone.

## Pull Request Requirements

Each Work Order PR should include:

- linked Work Order issue;
- concise summary;
- scope statement;
- non-goals statement;
- validation commands and results;
- review status;
- confirmation that the Phase 1.5 Claude review prompt was used;
- confirmation that no unresolved P0/P1 Claude findings remain;
- confirmation that no production Phase 2+ capability was introduced.

## Merge Policy

Work Order PRs may be squash-merged only when:

- local tests pass;
- CI checks pass;
- Claude review has no unresolved P0/P1 findings;
- PR scope matches only the current Work Order;
- no merge conflicts exist;
- no production Phase 2+ capability was introduced;
- spike dependencies, if any, are isolated.

The merge command should use:

```text
gh pr merge <PR_NUMBER> --squash --delete-branch
```

After merge:

```text
git checkout main
git pull --ff-only
```

## Phase Tag Convention

Phase tags should use stable lowercase names:

```text
phase-<major-or-major.minor>-<short-kebab-description>
```

Examples:

```text
phase-1-core-package-system-mvp
phase-1.5-technical-spike-checkpoint
phase-2-persistent-registry
```

The Phase 1.5 tag can only be created after:

1. WO9 is squash-merged into `main`.
2. `main` is synced with `git pull --ff-only`.
3. `pytest` passes.
4. `ruff check .` passes when configured.
5. `aam --help` passes when available.
6. `dev_docs/review/phase_1_5_codex_final_review.md` exists.
7. `dev_docs/review/phase_1_5_claude_final_review.md` exists.
8. Both final reviews have no unresolved P0/P1 findings.
9. `dev_docs/phase1.5/phase_1_5_closeout_checklist.md` exists.
10. `git status --short` is clean.

Only then:

```text
git tag phase-1.5-technical-spike-checkpoint
git push origin phase-1.5-technical-spike-checkpoint
```

## Consequences

The repository now has a repeatable Work Order loop:

- issue defines scope;
- branch implements only that scope;
- PR records validation and review gates;
- CI checks the package, lint, tests, and installed CLI;
- Claude review blocks only unresolved P0/P1 findings;
- squash merge preserves one mainline commit per Work Order;
- phase tag happens only after closeout.

Future phases should update templates if their review prompt or gates differ, but should keep the same principle: issue scope, service-boundary implementation, deterministic validation, AI review, CI, squash merge, final closeout, then tag.

## Non-goals

- No production deployment pipeline.
- No release automation beyond convention documentation.
- No branch protection changes in this ADR.
- No GitHub Actions matrix expansion beyond the Phase 1.5 baseline.
- No phase tag creation in WO7.
- No production Phase 2+ capability implementation.
