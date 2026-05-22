"""CLI MVP tests for Phase 1 workflows."""

from __future__ import annotations

import json
from pathlib import Path

from aam.cli.main import main

FIXTURES = Path(__file__).parent / "fixtures"


def _json_stdout(capsys) -> dict:
    return json.loads(capsys.readouterr().out)


def test_cli_init_creates_minimal_package(tmp_path: Path) -> None:
    package_root = tmp_path / "new-package"

    exit_code = main(["init", str(package_root)])

    assert exit_code == 0
    assert (package_root / "package.yaml").is_file()
    assert (package_root / "assets").is_dir()
    assert (package_root / "profiles").is_dir()


def test_cli_validate_reports_errors_with_nonzero_exit(capsys) -> None:
    exit_code = main(["validate", str(FIXTURES / "validator_problem_package")])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "ASSET_PATH_MISSING" in captured.out
    assert "BROKEN_PROFILE_INCLUDE_REFERENCE" in captured.out


def test_cli_index_json_outputs_registry_summary(capsys) -> None:
    exit_code = main(["index", str(FIXTURES / "valid_basic_package"), "--json"])

    payload = _json_stdout(capsys)
    assert exit_code == 0
    assert payload == {
        "asset_count": 2,
        "edge_count": 18,
        "node_count": 13,
        "package_count": 1,
        "profile_count": 1,
    }


def test_cli_list_assets_json_supports_filters(capsys) -> None:
    exit_code = main(
        [
            "list",
            "assets",
            str(FIXTURES / "valid_basic_package"),
            "--type",
            "agent",
            "--json",
        ]
    )

    payload = _json_stdout(capsys)
    assert exit_code == 0
    assert [asset["id"] for asset in payload["assets"]] == ["code-reviewer"]


def test_cli_list_profiles_json(capsys) -> None:
    exit_code = main(
        ["list", "profiles", str(FIXTURES / "valid_basic_package"), "--json"]
    )

    payload = _json_stdout(capsys)
    assert exit_code == 0
    assert [profile["id"] for profile in payload["profiles"]] == ["coding-review"]


def test_cli_show_asset_json_omits_file_content(capsys) -> None:
    exit_code = main(
        [
            "show",
            "asset",
            str(FIXTURES / "valid_basic_package"),
            "code-reviewer",
            "--json",
        ]
    )

    payload = _json_stdout(capsys)
    assert exit_code == 0
    assert payload["id"] == "code-reviewer"
    assert payload["content_hash"].startswith("sha256:")
    assert payload["dependencies"] == [
        "personal-agent-assets:coding-style-guide@0.1.0"
    ]
    assert "content" not in payload


def test_cli_show_card_json_outputs_asset_card(capsys) -> None:
    exit_code = main(
        [
            "show",
            "card",
            str(FIXTURES / "valid_basic_package"),
            "code-reviewer",
            "--json",
        ]
    )

    payload = _json_stdout(capsys)
    assert exit_code == 0
    assert payload["id"] == "code-reviewer"
    assert payload["title"] == "Code Reviewer"
    assert payload["content_hash"].startswith("sha256:")


def test_cli_graph_export_json_outputs_nodes_and_edges(capsys) -> None:
    exit_code = main(
        [
            "graph",
            "export",
            str(FIXTURES / "valid_basic_package"),
            "--json",
        ]
    )

    payload = _json_stdout(capsys)
    assert exit_code == 0
    assert "nodes" in payload
    assert "edges" in payload
    assert any(node["type"] == "asset" for node in payload["nodes"])
    assert any(edge["type"] == "asset_depends_on_asset" for edge in payload["edges"])
