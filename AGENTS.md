# AGENTS.md

## Project

This repository implements Agent Asset Management.

AAM is a local-first, private-first Agent Asset Registry and Agent-facing Discovery and Assembly Layer.

It is not:
- an agent runtime
- a pip/npm-style package manager
- a public marketplace
- a tool that executes external agents

## Current Phase

We are implementing Phase 1: Core Package System MVP.

The goal is to build the minimum package, manifest, validation, in-memory registry, asset card projection, graph JSON projection, and CLI foundation.

## Phase 1 Non-goals

Do not implement:
- GitHub importer
- persistent registry database
- HTTP API
- MCP server
- Web UI
- Assembly Plan
- Package Lock
- materialization
- asset editing
- semantic search
- dashboard
- graph visualization UI

## Architecture Rules

- Manifest is the source of truth.
- Registry is a query projection.
- CLI must call services, not duplicate business logic.
- Asset Card projection must be deterministic and must not depend on LLM summarization.
- Trust status and permissions must come from manifest/defaults, not content inference.
- Graph projection in Phase 1 is lightweight JSON only.
- Keep Phase 1 small in functionality but complete in foundational metadata.

## Preferred Implementation Style

- Use typed Python models.
- Keep parser, validator, registry builder, query service, graph projection, and CLI separated.
- Add tests for every work order.
- Do not silently ignore validation errors.
- Prefer deterministic outputs for JSON and snapshot tests.