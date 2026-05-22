# Phase 1 Quickstart

This guide demonstrates the Phase 1 Agent Asset Management package flow:
create a package, validate it, build a temporary in-memory registry, inspect
assets and Asset Cards, and export lightweight graph JSON.

## Install For Local Development

From the repository root:

```bash
python -m pip install -e ".[dev]"
python -m aam.cli --help
```

You can also use the console script when installed:

```bash
aam --help
```

## Create A Package Skeleton

```bash
python -m aam.cli init ./my-agent-package
```

The command creates a minimal `package.yaml` plus starter directories. It does
not overwrite an existing `package.yaml`.

## Validate A Package

```bash
python -m aam.cli validate ./examples/personal-agent-assets
```

Validation parses `package.yaml`, checks asset paths, resolves references, and
prints errors or warnings. Validation errors return a non-zero exit code.

For machine-readable output:

```bash
python -m aam.cli validate ./examples/personal-agent-assets --json
```

## Build A Temporary Registry

Phase 1 does not persist a registry. Each command rebuilds an in-memory
projection from the package root.

```bash
python -m aam.cli index ./examples/personal-agent-assets --json
```

This prints package, asset, profile, node, and edge counts.

## List Assets And Profiles

```bash
python -m aam.cli list assets ./examples/personal-agent-assets --json
python -m aam.cli list profiles ./examples/personal-agent-assets --json
```

Asset listing supports basic filters:

```bash
python -m aam.cli list assets ./examples/personal-agent-assets --type agent
python -m aam.cli list assets ./examples/personal-agent-assets --tag coding
python -m aam.cli list assets ./examples/personal-agent-assets --trust trusted
python -m aam.cli list assets ./examples/personal-agent-assets --lifecycle active
python -m aam.cli list assets ./examples/personal-agent-assets --target-host codex
```

## Show Asset Metadata

```bash
python -m aam.cli show asset ./examples/personal-agent-assets code-reviewer --json
```

The output includes manifest metadata, content hash, dependencies, and reverse
dependencies. It does not print the full asset file content by default.

## Show An Asset Card

```bash
python -m aam.cli show card ./examples/personal-agent-assets code-reviewer --json
```

Asset Cards are deterministic projections from manifest fields and content
hashes. Phase 1 does not use LLM summarization.

## Export Graph JSON

```bash
python -m aam.cli graph export ./examples/personal-agent-assets --json
```

The graph export is a lightweight JSON projection of package, asset, profile,
tag, target host, source, trust status, lifecycle status, dependency, and
include relationships.

## Phase 1 limitations

- No GitHub importer.
- No persistent registry database.
- No HTTP API.
- No MCP server.
- No Web UI.
- No Assembly Plan or Package Lock.
- No materialization workflow.
- No asset editing.
- No semantic search.
- No dashboard or graph visualization UI.

## Preparing For The Next Phase

Phase 1 intentionally keeps the package system local-first and small. Later
phases can add persistence, import workflows, policy gates, materialization, and
API surfaces on top of these foundations without changing the manifest-first
contract.
