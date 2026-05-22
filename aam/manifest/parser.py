"""YAML manifest parser for Phase 1 package manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError
from yaml import YAMLError

from aam.models.manifest import PackageManifest

PACKAGE_MANIFEST_FILENAME = "package.yaml"


class ManifestParseError(ValueError):
    """Raised when a package manifest cannot be parsed into typed models."""

    def __init__(self, message: str, path: Path) -> None:
        super().__init__(message)
        self.path = path


def parse_manifest(package_root: str | Path) -> PackageManifest:
    """Read package.yaml from a package root and return a typed manifest."""
    root = Path(package_root)
    manifest_path = root / PACKAGE_MANIFEST_FILENAME
    if not manifest_path.is_file():
        raise ManifestParseError(
            f"{PACKAGE_MANIFEST_FILENAME} not found at {manifest_path}",
            manifest_path,
        )

    raw_manifest = _read_yaml_mapping(manifest_path)
    try:
        return PackageManifest.model_validate(raw_manifest)
    except ValidationError as exc:
        details = _format_validation_errors(exc)
        raise ManifestParseError(
            f"Invalid manifest schema in {manifest_path}: {details}",
            manifest_path,
        ) from exc


def _read_yaml_mapping(manifest_path: Path) -> dict[str, Any]:
    try:
        with manifest_path.open("r", encoding="utf-8") as manifest_file:
            loaded = yaml.safe_load(manifest_file)
    except YAMLError as exc:
        raise ManifestParseError(
            f"Invalid YAML in {manifest_path}: {exc}",
            manifest_path,
        ) from exc
    except OSError as exc:
        raise ManifestParseError(
            f"Unable to read {manifest_path}: {exc}",
            manifest_path,
        ) from exc

    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        message = "document root must be a mapping"
        raise ManifestParseError(
            f"Invalid manifest schema in {manifest_path}: {message}",
            manifest_path,
        )
    return loaded


def _format_validation_errors(error: ValidationError) -> str:
    messages: list[str] = []
    for issue in error.errors():
        location = ".".join(str(part) for part in issue["loc"])
        messages.append(f"{location}: {issue['msg']}")
    return "; ".join(messages)
