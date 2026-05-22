"""SHA-256 content hashing for asset files."""

from __future__ import annotations

import hashlib
from pathlib import Path


def compute_content_hash(path: str | Path) -> str:
    """Return the Phase 1 SHA-256 content hash for a file."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as asset_file:
        for chunk in iter(lambda: asset_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"
