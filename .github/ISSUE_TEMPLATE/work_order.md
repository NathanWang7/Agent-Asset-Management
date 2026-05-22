---
name: Work Order
about: Track a scoped AAM work order
title: "WO<N> — <title>"
labels: "work-order,docs"
assignees: ""
---

## Goal

Describe the goal of this Work Order.

## Scope

List the files, systems, and decisions that are in scope.

## Deliverables

- 

## Acceptance Criteria

- 

## Non-goals

- 
- Do not implement production Phase 2+ capabilities unless this Work Order explicitly scopes them.

## Test commands

- `pytest`
- `ruff check .` if configured
- `aam --help` or equivalent CLI help command if available
- Focused validation:

## Review

- Use the correct phase review prompt.
- Classify findings as P0/P1/P2/P3.
- Fix unresolved P0/P1 findings before merge.

## Warning

Do not implement production Phase 2+ capabilities in this Work Order. Keep scope limited to the current issue.
