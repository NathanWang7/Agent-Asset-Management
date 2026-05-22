# ADR 0005: Frontend and Graph Stack

## Status

Accepted (Phase 1.5), 2026-05-22.

## Decision

Use React + Vite + TypeScript as the default stack for the future Phase 6 Web Asset Browser.

Use Cytoscape.js as the primary renderer for the future Phase 7 relationship graph.

Reserve React Flow only for optional future explanatory/flow diagrams, such as assembly-plan flows, approval flows, or onboarding diagrams. React Flow should not be the primary relationship graph renderer.

Do not create a production Web UI, graph visualization UI, frontend package, Vite project, Cytoscape probe, or React Flow probe in Phase 1.5.

## Source Check

Current official documentation reviewed for this ADR:

- React documentation: <https://react.dev/>
- Vite documentation: <https://vite.dev/guide/>
- Next.js documentation: <https://nextjs.org/>
- Cytoscape.js documentation: <https://js.cytoscape.org/>
- React Flow documentation: <https://reactflow.dev/>
- Sigma.js documentation: <https://www.sigmajs.org/docs/>
- AntV G6 documentation: <https://g6.antv.antgroup.com/en/manual/introduction/>

React's official documentation describes React as a component-based library for web and native user interfaces. Vite's official documentation describes Vite as a modern build tool with a fast dev server, HMR, optimized production build, TypeScript templates including `react-ts`, and static-site deployment support.

Cytoscape.js describes itself as an open-source graph theory/network library for visualization and analysis, with graph algorithms, selectors, layouts, JSON serialization, desktop/mobile gestures, and headless operation. React Flow describes itself as a React component for node-based editors and interactive diagrams. Sigma.js focuses on WebGL rendering for large graphs. G6 describes itself as a graph visualization engine with drawing, layout, analysis, interaction, animation, WebGPU/WASM acceleration, and 3D capabilities.

## Context

AAM's future frontend phases are separated:

- Phase 6: Web Asset Browser.
- Phase 7: Dashboard and Relationship Graph MVP.

The Web Asset Browser should be a local-first interface over stable AAM services. It should not become a public marketplace or remote team workspace. The relationship graph should render package, asset, profile, dependency, source, trust, lifecycle, tag, target host, and later assembly/lock relationships from registry projections.

Phase 1 already has lightweight deterministic graph JSON. Phase 1.5 should decide stack direction without creating production UI scaffolding.

## Frontend Alternatives

### React + Vite + TypeScript

React + Vite + TypeScript provides a client-side app stack with fast local development, explicit frontend build tooling, TypeScript contracts, and no required server framework.

Pros:

- Matches the need for a local Web Asset Browser that can call future local API services.
- Keeps frontend package boundaries simple and easy to isolate in a later phase.
- Vite supports a `react-ts` template and optimized static production builds.
- Avoids server-side rendering and deployment concerns before AAM has a production API.
- TypeScript can mirror stable API/registry DTOs when those contracts exist.

Cons:

- Does not provide a full-stack routing/data framework by default.
- Future routing, query caching, and state management choices remain open.
- Requires later decisions about component library, test runner, accessibility checks, and packaging.

Decision: choose React + Vite + TypeScript for Phase 6.

### Next.js

Next.js is a full-stack React framework with routing, server rendering, streaming, route handlers, middleware, and server actions.

Pros:

- Strong full-stack framework.
- Useful when server rendering, server routes, or production web deployment are core requirements.
- Mature ecosystem and documentation.

Cons:

- Adds server/runtime concepts before AAM needs a production web server.
- Could blur the boundary between local API services and frontend concerns.
- More deployment and framework surface than needed for a local-first asset browser.
- Server Components and route handlers are not required for Phase 6's expected local UI.

Decision: do not choose Next.js as the default Phase 6 stack. Reconsider only if later product requirements need server-side rendering, hosted/team web deployment, or full-stack web routes.

### Other Frontend Options

Vue, Svelte, Solid, and vanilla TypeScript are viable for some local tools.

Decision: do not choose them for AAM's default because React has the strongest alignment with React Flow as an optional explanatory diagram tool, common design-system ecosystems, and likely contributor familiarity. Vite keeps the frontend build system framework-light even with React.

## Graph Visualization Alternatives

### Cytoscape.js

Cytoscape.js is a graph theory/network library for visualization and analysis. It supports graph algorithms, layouts, selectors, JSON serialization/deserialization, gestures, and headless operation.

Pros:

- Best match for AAM's relationship graph domain: nodes, edges, graph queries, graph algorithms, dependency traversal, and graph JSON.
- Can consume deterministic graph projections naturally.
- Supports layout and interaction needs for package/asset/profile/dependency graphs.
- Mature project with extensive docs and examples.
- Framework-agnostic enough to integrate into React without making React own graph semantics.

Cons:

- React integration requires a wrapper or custom component boundary.
- Very large graphs may still require performance tuning or a future specialized renderer.
- Styling/layout design remains nontrivial and should be tested with real AAM graph data.

Decision: use Cytoscape.js as the primary relationship graph renderer for Phase 7.

### React Flow

React Flow is a React component for node-based editors and interactive diagrams, with built-in dragging, zooming, panning, selection, and custom React nodes.

Pros:

- Excellent for editable flows, process diagrams, and explanatory node UIs.
- Easy to compose with React components.
- Useful for visualizing assembly-plan steps, approval flows, or onboarding explanations.

Cons:

- It is not primarily a graph-theory library.
- Relationship graph traversal, graph algorithms, and large network layouts are not its core domain.
- It encourages custom node-editor semantics that could distract from AAM's registry relationship graph.

Decision: reserve React Flow for optional future explanatory/flow diagrams only. Do not use it as the primary Phase 7 relationship graph renderer.

### Sigma.js

Sigma.js is a WebGL graph renderer focused on visualizing large graphs efficiently, built on Graphology.

Pros:

- Strong future option for large graph rendering.
- WebGL performance for thousands of nodes/edges.
- Framework-agnostic.

Cons:

- More focused on rendering/exploration than graph editing or AAM-specific relationship semantics.
- Adds Graphology data model considerations.
- Phase 7 MVP should first prove relationship semantics before optimizing for large-scale rendering.

Decision: keep Sigma.js as a future high-scale rendering option if Cytoscape.js performance becomes a concrete blocker.

### AntV G6

G6 is a broad graph visualization engine with layouts, interactions, animation, customization, WebGPU/WASM acceleration, and 3D support.

Pros:

- Powerful graph visualization toolkit.
- Rich built-in layouts and interactions.
- Strong option for advanced/custom graph scenes.

Cons:

- Larger conceptual surface than needed for AAM's first relationship graph.
- More broad visualization engine than graph-theory-oriented registry projection tool.
- 3D and advanced scene capabilities are outside Phase 7 MVP needs.

Decision: keep G6 as a credible future alternative, but do not choose it as the default.

## Probe Decision

No React/Vite, Cytoscape.js, React Flow, Sigma.js, or G6 probe is added in Phase 1.5.

Rationale:

- The official docs answer the stack viability questions.
- AAM does not yet have Phase 6/7 API contracts or production graph data volume.
- A throwaway Vite app could be mistaken for the production Web UI package.
- Probe dependencies would need isolation and cleanup with little risk reduction.
- Phase 6/7 should create focused prototypes when real service contracts and UI requirements exist.

If a later spike is needed, it must live under `spikes/phase1.5/` or the relevant future phase spike directory and must not affect production build tooling.

## Phase Boundaries

Phase 6 Web Asset Browser should decide:

- frontend package location;
- API client boundaries;
- route/view structure;
- component library;
- accessibility checks;
- browser-based test strategy;
- local dev server conventions;
- packaging and static build output.

Phase 7 Relationship Graph should decide:

- Cytoscape.js integration boundary;
- graph DTO contract from registry/API;
- layout strategy;
- viewport and selection behavior;
- filtering/search interaction;
- handling large graphs and degraded rendering;
- snapshot/visual regression strategy.

## Consequences

Future implementation specs should:

- keep frontend dependencies out of Python runtime dependencies;
- isolate frontend package management from the Phase 1 Python package;
- treat graph rendering as a view over registry/API graph projections;
- avoid duplicating graph projection business logic in React components;
- test graph data contracts separately from renderer behavior;
- revisit Sigma.js or G6 only if Cytoscape.js hits concrete performance or feature blockers.

## Non-goals

- No production Web UI in Phase 1.5.
- No graph visualization UI in Phase 1.5.
- No production frontend package in Phase 1.5.
- No React, Vite, Cytoscape.js, React Flow, Sigma.js, or G6 dependency added in Phase 1.5.
- No frontend or graph probe code in Phase 1.5; no blocker was found.
- No dashboard.
- No team workspace.
- No semantic search.
