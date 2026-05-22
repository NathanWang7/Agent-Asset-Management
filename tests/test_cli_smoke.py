"""Smoke tests for the placeholder AAM CLI."""

from __future__ import annotations

import subprocess
import sys


def test_cli_help_runs() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "aam.cli", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Agent Asset Management" in result.stdout
