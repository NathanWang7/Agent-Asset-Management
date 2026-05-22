"""Tests for Phase 1 asset content hashing."""

from __future__ import annotations

from pathlib import Path

from aam.hash.content_hash import compute_content_hash


def test_same_file_produces_same_hash(tmp_path: Path) -> None:
    asset_path = tmp_path / "asset.md"
    asset_path.write_bytes(b"stable content\n")

    first_hash = compute_content_hash(asset_path)
    second_hash = compute_content_hash(asset_path)

    assert first_hash == second_hash


def test_changed_file_produces_different_hash(tmp_path: Path) -> None:
    asset_path = tmp_path / "asset.md"
    asset_path.write_bytes(b"first content\n")
    first_hash = compute_content_hash(asset_path)

    asset_path.write_bytes(b"changed content\n")
    second_hash = compute_content_hash(asset_path)

    assert first_hash != second_hash


def test_hash_format_uses_sha256_prefix(tmp_path: Path) -> None:
    asset_path = tmp_path / "asset.md"
    asset_path.write_bytes(b"content\n")

    content_hash = compute_content_hash(asset_path)

    assert content_hash.startswith("sha256:")
    assert len(content_hash.removeprefix("sha256:")) == 64


def test_empty_file_produces_valid_hash(tmp_path: Path) -> None:
    asset_path = tmp_path / "empty.md"
    asset_path.write_bytes(b"")

    content_hash = compute_content_hash(asset_path)

    assert content_hash.startswith("sha256:")
    assert len(content_hash.removeprefix("sha256:")) == 64
