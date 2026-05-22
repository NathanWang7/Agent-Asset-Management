# ADR 0003: API and MCP Framework

## Status

Accepted (Phase 1.5), 2026-05-22.

## Decision

Use FastAPI as the default framework for the future Phase 4A Local Agent Gateway API.

Use the official MCP Python SDK as the default framework for the future Phase 4B MCP Server.

Use stdio as the first MCP transport target for AAM's local integration path. Treat Streamable HTTP as a later transport option when AAM needs a production-style HTTP MCP deployment or multi-client process boundary.

Do not implement a production API server, production MCP server, registry business logic in MCP, assembly business logic in MCP, or framework probe code in Phase 1.5.

This confirms the Phase 1.5 implementation spec's recommended defaults unless a spike finds a concrete blocker. No concrete blocker was found.

## Source Check

Current official documentation reviewed for this ADR:

- FastAPI documentation: <https://fastapi.tiangolo.com/>
- Litestar documentation: <https://docs.litestar.dev/latest/>
- MCP SDK list: <https://modelcontextprotocol.io/docs/sdk>
- MCP Python SDK documentation: <https://py.sdk.modelcontextprotocol.io/server/>
- MCP transport specification: <https://modelcontextprotocol.io/docs/concepts/transports>

The official FastAPI documentation describes FastAPI as a Python API framework based on standard type hints, with OpenAPI and JSON Schema compatibility, automatic validation, conversion, and interactive documentation.

The official Litestar documentation describes Litestar as a powerful, flexible, performant, opinionated ASGI framework with plugins, dependency injection, security primitives, OpenAPI generation, middleware, CLI support, and multiple optional extras.

The MCP SDK list identifies the Python SDK as a Tier 1 official SDK. The MCP transport documentation defines stdio and Streamable HTTP as standard transports and states that clients should support stdio whenever possible.

## Context

AAM's future Agent Gateway and MCP surfaces must expose controlled discovery and assembly capabilities without bypassing manifest, registry, trust, visibility, permission, dependency, policy, or materialization boundaries.

Phase 1 currently has:

- typed Python models;
- parser and validator services;
- an in-memory registry builder;
- query service boundaries;
- deterministic Asset Card and graph projections;
- CLI command handlers that call services.

Phase 4A and Phase 4B should wrap those service boundaries. They should not reimplement parser, validator, registry, profile closure, assembly, lockfile, materialization, or policy logic.

Phase 1.5 is a decision checkpoint. It should choose a direction, not start the production API or MCP implementation.

## API Alternatives

### FastAPI

FastAPI is an ASGI API framework centered on Python type hints, Pydantic models, request/response validation, OpenAPI generation, interactive API docs, and Uvicorn/Starlette ecosystem compatibility.

Pros:

- Strong fit with AAM's typed Python model style.
- OpenAPI generation supports future agent-facing and human-debuggable local API contracts.
- Large ecosystem and common deployment/testing patterns.
- Good match for Pydantic-based request and response contracts.
- Straightforward local-only development server story for Phase 4A.

Cons:

- Adds production runtime dependencies in Phase 4A.
- Async/sync boundaries must be deliberate around SQLite and file IO.
- Dependency injection should be kept simple to avoid hiding service boundaries.

Decision: use FastAPI as the default Phase 4A API framework.

### Litestar

Litestar is a performant ASGI framework with first-class dependency injection, plugins, OpenAPI support, security primitives, DTOs, repositories, and a more opinionated application structure.

Pros:

- Strong framework capabilities and OpenAPI support.
- More batteries included for larger applications.
- Good performance and an active project.

Cons:

- Larger conceptual surface than AAM needs for its first local API.
- DTO/repository/plugin patterns could pull Phase 4A into framework architecture before the service contracts are stable.
- Smaller mindshare in AI-agent tooling examples than FastAPI.

Decision: keep Litestar as a credible fallback, but do not choose it for the default Phase 4A API.

### Starlette Directly

Starlette is the lower-level ASGI foundation under FastAPI.

Pros:

- Minimal and explicit.
- Good control over routing and lifecycle.
- Fewer framework abstractions.

Cons:

- AAM would need to assemble more validation, OpenAPI, request/response model, and documentation conventions itself.
- Less aligned with the existing Pydantic model investment than FastAPI.

Decision: do not use Starlette directly for the default API, though FastAPI's Starlette foundation remains useful.

### Flask or Other WSGI Frameworks

Pros:

- Mature ecosystem and simple mental model.

Cons:

- Less natural for async agent-facing workflows, streaming, and modern typed OpenAPI contracts.
- More manual schema/validation work.

Decision: not recommended for the Local Agent Gateway API.

## MCP Alternatives

### Official MCP Python SDK

The official MCP Python SDK supports MCP server/client development, FastMCP ergonomics, resources, tools, prompts, stdio, and Streamable HTTP examples.

Pros:

- Official Tier 1 SDK.
- Tracks protocol evolution directly.
- Supports stdio, the first local integration target.
- Provides MCP-native concepts rather than requiring AAM to hand-roll protocol details.
- Can keep MCP as a thin adapter over AAM services.

Cons:

- MCP is evolving quickly, so Phase 4B should pin versions and review transport/security notes at implementation time.
- The SDK's convenience abstractions must not become AAM business logic.

Decision: use the official MCP Python SDK for Phase 4B.

### Hand-Rolled MCP Implementation

Pros:

- Maximum control over protocol surface.
- No SDK dependency.

Cons:

- High protocol drift risk.
- More test burden.
- Poor use of official SDK maintenance.

Decision: reject for Phase 4B unless a concrete SDK blocker appears.

### Third-Party MCP Frameworks or API-to-MCP Bridges

Pros:

- May reduce boilerplate for simple tools.
- May bridge HTTP and MCP endpoints from one declaration.

Cons:

- Additional dependency and protocol lag risk.
- Could blur AAM's boundary between API contracts and MCP tools.
- Not necessary before AAM has stable Phase 3 and Phase 4A services.

Decision: do not choose a third-party MCP framework for Phase 4B default.

## API and MCP Relationship

Phase 4A Local Agent Gateway API and Phase 4B MCP Server are separate adapters over shared AAM services.

Phase 4A should provide local HTTP endpoints for controlled discovery, Asset Card reads, explain/validate, assembly requests, materialization preview, health, and diagnostics.

The Phase 4A API should fail closed by default. Its first implementation should bind only to localhost, avoid permissive CORS defaults, and treat any remote/shared access model as a separate future security design.

Phase 4B should expose MCP resources/tools/prompts that call the same underlying services. MCP must not implement registry or assembly business logic. It should convert MCP requests to service calls, enforce the same policy boundaries, and return MCP-appropriate responses.

The relationship should be:

```text
CLI / API / MCP
  -> application services
  -> registry/query/profile/assembly/lock/materialization services
  -> manifest, registry store, policy, event placeholders
```

Not:

```text
MCP
  -> scans packages directly
  -> builds registry independently
  -> assembles assets independently
  -> bypasses policy because a client asked for a tool call
```

## Transport Boundary

Phase 4B should target stdio first because AAM is local-first and private-first, and stdio is the simplest local MCP integration model. The MCP transport specification defines stdio as standard input/output communication and states that clients should support stdio whenever possible.

Streamable HTTP should be reconsidered when AAM needs a production-style MCP deployment, remote process boundary, multi-client server, resumability, or browser/client transport. The MCP Python SDK documentation currently identifies Streamable HTTP as the recommended transport for production deployments, but Phase 4B's first AAM MCP integration is a local server adapter, not a public or remote production service.

SSE should not be a new default. Current MCP Python SDK documentation notes that SSE transport is being superseded by Streamable HTTP.

## Probe Decision

No FastAPI or MCP probe is added in Phase 1.5.

Rationale:

- Official docs answer the framework viability questions.
- AAM does not yet have Phase 3 profile/assembly/lock services for realistic endpoint/tool probes.
- A toy FastAPI or MCP server would be throwaway code and could look like production scaffolding.
- Adding spike dependencies would create avoidable dependency-isolation work with little risk reduction.

Phase 4A and Phase 4B implementation specs should include minimal tests and prototypes in their own branches when real service contracts exist.

## Consequences

Phase 4A implementation specs should define:

- FastAPI dependency and version policy;
- local-only binding defaults;
- request/response Pydantic models;
- OpenAPI contract stability expectations;
- service dependency wiring;
- failure and degraded-mode response shapes;
- event placeholder emission boundaries;
- test strategy using FastAPI test clients.

Phase 4B implementation specs should define:

- official MCP Python SDK dependency and version policy;
- stdio server entry point;
- MCP resource/tool/prompt inventory;
- policy and service boundary enforcement;
- error handling and degraded-mode behavior;
- event placeholder emission boundaries;
- tests using SDK client/session helpers.

Both phases should keep CLI, API, and MCP as adapters over service boundaries.

The Phase 3 minimal reason-code explain/validate versus Phase 4A full explain/validate API boundary is assigned to the composition and assembly boundary work in WO5. This ADR only records the API/MCP framework and adapter boundary.

## Non-goals

- No production HTTP API server in Phase 1.5.
- No production MCP server in Phase 1.5.
- No FastAPI, Litestar, MCP SDK, or third-party MCP dependency added in Phase 1.5.
- No API or MCP probe code unless a concrete blocker appears; no blocker was found.
- No registry, profile closure, assembly, lockfile, or materialization business logic in MCP.
- No Web UI.
- No graph visualization UI.
- No remote/shared gateway design.
