from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class RestoreError(RuntimeError):
    """Raised when a restore run cannot complete successfully."""


@dataclass(frozen=True)
class RestoreResult:
    """Summary of one successful restore run."""

    backup_file: Path
    restore_dataset: str


class RestoreService:
    """Replay a backup stream file into a restore dataset."""

    def __init__(self, zfs_ops) -> None:
        self._zfs_ops = zfs_ops

    def run(self, *, backup_file: str | Path, restore_dataset: str) -> RestoreResult:
        """Restore one backup file into the configured dataset."""
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise RestoreError(f"Backup file does not exist: {backup_path}")
        if backup_path.stat().st_size <= 0:
            raise RestoreError(f"Backup file is empty: {backup_path}")
        target_dataset = restore_dataset.strip()
        if not target_dataset:
            raise RestoreError("restore dataset must be a non-empty string")
        if self._zfs_ops.dataset_exists(target_dataset):
            raise RestoreError(
                f"Restore target dataset already exists: {target_dataset}. "
                "Use a fresh target or destroy the old restore dataset first."
            )

        self._zfs_ops.receive_from_file(backup_path, target_dataset)
        return RestoreResult(backup_file=backup_path, restore_dataset=target_dataset)
