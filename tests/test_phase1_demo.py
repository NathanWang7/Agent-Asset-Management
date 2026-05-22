"""Tests for the Phase 1 quickstart demo package."""

from __future__ import annotations

import json
from pathlib import Path

from aam.cli.main import main

ROOT = Path(__file__).parents[1]
DOC = ROOT / "docs" / "phase1_quickstart.md"
EXAMPLE = ROOT / "examples" / "personal-agent-assets"


def _json_stdout(capsys) -> dict:
    return json.loads(capsys.readouterr().out)


def test_quickstart_documents_phase_1_limitations() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "Phase 1 limitations" in text
    assert "No GitHub importer" in text
    assert "No HTTP API" in text
    assert "No MCP server" in text
    assert "No Web UI" in text


def test_example_package_validates_and_indexes(capsys) -> None:
    assert main(["validate", str(EXAMPLE)]) == 0
    capsys.readouterr()

    assert main(["index", str(EXAMPLE), "--json"]) == 0
    payload = _json_stdout(capsys)
    assert payload["package_count"] == 1
    assert payload["asset_count"] == 2
    assert payload["profile_count"] == 1


def test_example_package_cli_demo_commands(capsys) -> None:
    assert main(["list", "assets", str(EXAMPLE), "--json"]) == 0
    assets_payload = _json_stdout(capsys)
    assert [asset["id"] for asset in assets_payload["assets"]] == [
        "code-reviewer",
        "coding-style-guide",
    ]

    assert main(["show", "card", str(EXAMPLE), "code-reviewer", "--json"]) == 0
    card_payload = _json_stdout(capsys)
    assert card_payload["title"] == "Code Reviewer"

    assert main(["graph", "export", str(EXAMPLE), "--json"]) == 0
    graph_payload = _json_stdout(capsys)
    assert graph_payload["nodes"]
    assert graph_payload["edges"]
