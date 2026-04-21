from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


_TIMESTAMP_PATTERN = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}"


class RetentionError(RuntimeError):
    """Raised when retention planning or deletion fails."""


@dataclass(frozen=True)
class RetentionResult:
    """Summary of which backup files were kept, deleted, or ignored."""

    retained_backups: tuple[Path, ...]
    deleted_backups: tuple[Path, ...]
    ignored_files: tuple[Path, ...] = ()


def _match_backup_name(path: Path, snapshot_prefix: str) -> bool:
    pattern = re.compile(rf"^{re.escape(snapshot_prefix)}_{_TIMESTAMP_PATTERN}\.zfs$")
    return bool(pattern.match(path.name))


def plan_retention(candidates: list[Path], *, snapshot_prefix: str, keep: int) -> RetentionResult:
    """Plan which valid backup files should be retained or deleted."""
    if keep <= 0:
        raise RetentionError("Retention keep-count must be a positive integer")

    matching = [path for path in candidates if _match_backup_name(path, snapshot_prefix)]
    ignored = [path for path in candidates if path not in matching]
    matching.sort(key=lambda path: path.name)

    if len(matching) <= keep:
        return RetentionResult(
            retained_backups=tuple(matching),
            deleted_backups=(),
            ignored_files=tuple(sorted(ignored, key=lambda path: path.name)),
        )

    split_index = len(matching) - keep
    return RetentionResult(
        retained_backups=tuple(matching[split_index:]),
        deleted_backups=tuple(matching[:split_index]),
        ignored_files=tuple(sorted(ignored, key=lambda path: path.name)),
    )


def apply_retention(backup_directory: str | Path, *, snapshot_prefix: str, keep: int) -> RetentionResult:
    """Delete the oldest eligible backup files until only the newest N remain."""
    backup_dir = Path(backup_directory)
    try:
        candidates = list(backup_dir.iterdir())
    except OSError as exc:
        raise RetentionError(f"Retention directory is not readable: {backup_dir}") from exc

    plan = plan_retention(candidates, snapshot_prefix=snapshot_prefix, keep=keep)
    for path in plan.deleted_backups:
        try:
            path.unlink()
        except OSError as exc:
            raise RetentionError(f"Failed to delete old backup file: {path}") from exc
    return plan
