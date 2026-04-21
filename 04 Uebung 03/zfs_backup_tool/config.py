from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


REQUIRED_FIELDS = (
    "source_dataset",
    "source_mountpoint",
    "backup_directory",
    "max_backups",
    "snapshot_prefix",
    "restore_dataset",
)


class ConfigError(ValueError):
    """Raised when configuration loading or validation fails."""


@dataclass(frozen=True)
class AppConfig:
    """Validated application configuration."""

    source_dataset: str
    source_mountpoint: str
    backup_directory: str
    max_backups: int
    snapshot_prefix: str
    restore_dataset: str


def load_config(path: str | Path) -> AppConfig:
    """Load and validate config from a JSON file."""
    config_path = Path(path)
    try:
        raw_text = config_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigError(f"Config file not found: {config_path}") from exc

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in config file: {config_path}") from exc

    if not isinstance(payload, dict):
        raise ConfigError("Configuration root must be a JSON object")

    missing_fields = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing_fields:
        joined = ", ".join(missing_fields)
        raise ConfigError(f"Missing required config field(s): {joined}")

    max_backups = payload["max_backups"]
    if not isinstance(max_backups, int) or max_backups <= 0:
        raise ConfigError("max_backups must be a positive integer")

    for field in REQUIRED_FIELDS:
        if field == "max_backups":
            continue
        value = payload[field]
        if not isinstance(value, str) or not value.strip():
            raise ConfigError(f"{field} must be a non-empty string")

    return AppConfig(
        source_dataset=payload["source_dataset"].strip(),
        source_mountpoint=payload["source_mountpoint"].strip(),
        backup_directory=payload["backup_directory"].strip(),
        max_backups=max_backups,
        snapshot_prefix=payload["snapshot_prefix"].strip(),
        restore_dataset=payload["restore_dataset"].strip(),
    )

