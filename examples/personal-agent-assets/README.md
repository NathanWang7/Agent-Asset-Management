# Personal Agent Assets Demo

This example package is used by the Phase 1 quickstart. It demonstrates a
small local package with two assets and one profile:

- `code-reviewer` is an agent asset that depends on `coding-style-guide`.
- `coding-style-guide` is an instruction asset shared by the demo profile.
- `coding-review` is a profile that includes both assets for the `codex`
  target host.

Run the demo from the repository root:

```bash
python -m aam.cli validate ./examples/personal-agent-assets
python -m aam.cli index ./examples/personal-agent-assets --json
python -m aam.cli list assets ./examples/personal-agent-assets --json
python -m aam.cli list profiles ./examples/personal-agent-assets --json
python -m aam.cli show asset ./examples/personal-agent-assets code-reviewer --json
python -m aam.cli show card ./examples/personal-agent-assets code-reviewer --json
python -m aam.cli graph export ./examples/personal-agent-assets --json
```

The package is intentionally small so it stays focused on the Phase 1 package,
validation, registry, Asset Card, and graph projection flow.
