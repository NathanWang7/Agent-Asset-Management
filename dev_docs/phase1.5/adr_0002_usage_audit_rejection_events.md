# ADR 0002: Usage, Audit, and Rejection Event Placeholders

## Status

Accepted (Phase 1.5), 2026-05-22.

## Decision

Phase 2 should reserve append-only placeholders for three event families:

- `UsageEvent`
- `AuditLog`
- `RejectionEvent`

These placeholders should be durable enough to support future Agent Gateway audit, rejection reason capture, recommendation signals, degraded-mode diagnostics, and materialization policy decision logging. Phase 2 should not implement recommendation learning, complex governance workflow, production event processing, or event-driven automation.

The default storage location should follow ADR 0001: workspace-scoped SQLite registry storage. Each event shape may include `workspace_id` for future diagnostics, migration, and cross-workspace reporting even though the database is workspace-scoped.

## Context

AAM's future phases need a way to explain and audit asset usage decisions without letting events become the source of truth. The manifest remains the source of truth for package declarations, and the registry remains a rebuildable query projection. Events are append-only observations about usage, decisions, failures, and rejections.

The event placeholders need to support future:

- Agent Gateway audit trails;
- rejection-to-governance loops;
- external agent recommendation feedback;
- degraded-mode diagnostics when AAM is unavailable or partially unavailable;
- materialization policy decision logs;
- debugging of why an asset was shown, hidden, rejected, or blocked.

Phase 1.5 defines shapes and semantics only. It must not implement production event writing code.

## Event Semantics

All three event families are append-only:

- Events are inserted, not updated in place.
- Correction should be represented by a later event that references the prior event.
- Deletion is reserved for future retention/privacy policy and should not be part of Phase 2 core behavior.
- Event ids must be stable unique ids generated at write time.
- Timestamps must be UTC ISO-8601 strings.
- Enum-like fields should use stable lowercase string values.
- Freeform metadata must be deterministic JSON when serialized.

Events are not policy by themselves. Future policy services may consume events, but Phase 2 should not let event history override manifest trust, visibility, lifecycle, permissions, or user approval rules.

## Minimal Shapes

The shapes below are pseudo-contracts for Phase 2 planning. They are not production Python models or migrations.

### UsageEvent

Purpose: record that a human or external agent attempted to discover, inspect, read, assemble, preview, lock, or materialize an asset/package/profile.

Recommended fields:

| Field | Required | Description |
| --- | --- | --- |
| `event_id` | Yes | Unique event id. |
| `workspace_id` | Yes | Future diagnostics/migration boundary. |
| `occurred_at` | Yes | UTC ISO-8601 timestamp. |
| `actor_type` | Yes | `human`, `agent`, `system`, or `unknown`. |
| `actor_id` | No | Stable local actor identifier when known. |
| `consumer_surface` | Yes | `cli`, `local_api`, `mcp`, `web_ui`, `materializer`, or `unknown`. |
| `operation` | Yes | Example: `asset_card_viewed`, `full_content_requested`, `profile_listed`, `assembly_requested`, `materialization_preview_requested`. |
| `package_id` | No | Related package id. |
| `asset_qualified_id` | No | Related asset id when applicable. |
| `profile_qualified_id` | No | Related profile id when applicable. |
| `request_id` | No | Correlation id for a gateway/API/MCP request. |
| `result` | Yes | `allowed`, `denied`, `degraded`, `failed`, or `unknown`. |
| `reason_codes` | Yes | Deterministic list of machine-readable reason codes. |
| `metadata` | Yes | Deterministic JSON object for non-contract diagnostic details. |

UsageEvent can later provide recommendation signals, but Phase 2 must not implement recommendation learning.

### AuditLog

Purpose: record security-relevant or governance-relevant decisions, especially where a future Agent Gateway, materialization flow, or policy gate needs accountability.

Recommended fields:

| Field | Required | Description |
| --- | --- | --- |
| `audit_id` | Yes | Unique audit event id. |
| `workspace_id` | Yes | Future diagnostics/migration boundary. |
| `occurred_at` | Yes | UTC ISO-8601 timestamp. |
| `actor_type` | Yes | `human`, `agent`, `system`, or `unknown`. |
| `actor_id` | No | Stable local actor identifier when known. |
| `request_id` | No | Correlation id for a gateway/API/MCP request. |
| `operation` | Yes | Example: `policy_checked`, `full_content_denied`, `materialization_approved`, `trust_override_requested`. |
| `target_type` | Yes | `package`, `asset`, `profile`, `assembly_plan`, `package_lock`, `materialization`, or `workspace`. |
| `target_id` | No | Stable id for the target when available. |
| `decision` | Yes | `allow`, `deny`, `warn`, `require_approval`, `degrade`, or `unknown`. |
| `policy_snapshot_ref` | No | Future pointer to policy snapshot/lock context. |
| `reason_codes` | Yes | Deterministic list of machine-readable reason codes. |
| `metadata` | Yes | Deterministic JSON object for non-contract diagnostic details. |

AuditLog is for accountability and diagnostics. It must not become a mutable workflow state table.

### RejectionEvent

Purpose: capture why a user or policy rejected an asset, recommendation, assembly plan, profile delta, lock, materialization preview, or risky action.

Recommended fields:

| Field | Required | Description |
| --- | --- | --- |
| `rejection_id` | Yes | Unique rejection event id. |
| `workspace_id` | Yes | Future diagnostics/migration boundary. |
| `occurred_at` | Yes | UTC ISO-8601 timestamp. |
| `actor_type` | Yes | `human`, `agent`, `system`, or `unknown`. |
| `actor_id` | No | Stable local actor identifier when known. |
| `request_id` | No | Correlation id for a gateway/API/MCP request. |
| `rejected_target_type` | Yes | `asset`, `profile`, `assembly_plan`, `package_lock`, `materialization`, `recommendation`, or `unknown`. |
| `rejected_target_id` | No | Stable id for the rejected target when available. |
| `rejection_reason_code` | Yes | Example: `trust_too_low`, `permission_too_broad`, `wrong_host`, `irrelevant`, `duplicate`, `stale`, `user_preference`. |
| `follow_up_action` | No | `ignore_once`, `review_now`, `mark_sandbox_only`, `block_asset`, `none`, or future value. |
| `freeform_note` | No | Human note. Not used for automatic policy decisions in Phase 2. |
| `metadata` | Yes | Deterministic JSON object for non-contract diagnostic details. |

RejectionEvent supports the future rejection-to-governance loop, but Phase 2 should only capture placeholders. It should not implement governance workflow, automatic trust changes, or recommendation model updates.

## Relationship to Future Phases

### Phase 2

Phase 2 may reserve tables or collections for these event families. It should not make event writing mandatory for core registry rebuilds.

If Phase 2 implements minimal event insertion for diagnostics, it must be isolated behind a service boundary and must not affect manifest validation, registry rebuild correctness, or CLI query results.

### Phase 3

Profile closure, assembly planning, package lock, and materialization preview may produce reason codes that later feed UsageEvent, AuditLog, or RejectionEvent records. Phase 3 should focus on minimal explain/validate reason codes, not full event analytics.

### Phase 4A

The Local Agent Gateway API should become the first major event producer. Gateway operations should use request ids and reason codes so audit/rejection events can be correlated with agent-facing decisions.

### Phase 4B

The MCP server should wrap stable services and may emit events through those services. MCP must not implement independent registry, assembly, or governance business logic.

### Later Governance and Recommendation Work

Future governance workflows may consume rejection events to offer actions such as review, sandbox, block, or ignore. Future recommendation systems may consume usage and rejection signals. Those are explicit non-goals for Phase 2 and Phase 1.5.

## Rationale

The three-event split keeps the placeholder model small:

- UsageEvent answers what was attempted and what happened.
- AuditLog answers what policy/security decision was made.
- RejectionEvent answers why something was rejected and what follow-up might be appropriate.

This avoids a single overloaded event table while keeping all three families simple enough for Phase 2 to reserve without building a full governance subsystem.

Append-only semantics preserve auditability and make degraded-mode diagnostics easier. Including `workspace_id` now is cheap and prevents future migration pain if reporting or migration tools need to correlate event exports across workspaces.

## Consequences

Future implementation specs should define:

- exact table names and columns;
- id generation strategy;
- allowed reason-code vocabulary;
- correlation id handling;
- retention and privacy rules;
- deterministic JSON serialization for metadata;
- service boundary for event insertion;
- tests proving events do not override manifest-derived trust, visibility, lifecycle, permissions, or validation.

Future implementation specs should avoid:

- using events as mutable workflow state;
- deriving trust status from event history in Phase 2;
- letting event capture failures break core registry queries;
- putting event-writing code directly in CLI command handlers.

## Non-goals

- No production event writing code in Phase 1.5.
- No production event store implementation in Phase 1.5.
- No recommendation learning.
- No automatic trust or lifecycle updates from events.
- No complex governance workflow.
- No Agent Gateway API.
- No MCP server.
- No materialization approval workflow.
- No persistent registry implementation beyond placeholder planning.
