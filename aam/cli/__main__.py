"""Module entrypoint for `python -m aam.cli`."""

from __future__ import annotations

from aam.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
