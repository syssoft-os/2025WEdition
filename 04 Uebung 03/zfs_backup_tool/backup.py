from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from zfs_backup_tool.config import AppConfig
from zfs_backup_tool.retention import RetentionError, apply_retention


class BackupError(RuntimeError):
    """Raised when a backup run cannot complete successfully."""


@dataclass(frozen=True)
class BackupResult:
    """Summary of one successful backup run."""

    snapshot_name: str
    backup_file: Path
    deleted_backups: tuple[Path, ...] = ()
    source_snapshot_cleanup: str = "kept"


class BackupService:
    """Orchestrate one snapshot-to-file backup run."""

    def __init__(self, config: AppConfig, zfs_ops, clock=None) -> None:
        self._config = config
        self._zfs_ops = zfs_ops
        self._clock = clock or self._default_timestamp

    @staticmethod
    def _default_timestamp() -> str:
        """Return a sortable timestamp for snapshots and file names."""
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def run(self) -> BackupResult:
        """Run exactly one backup pass."""
        if not self._zfs_ops.dataset_exists(self._config.source_dataset):
            raise BackupError(f"Configured source dataset does not exist: {self._config.source_dataset}")

        timestamp = self._clock()
        snapshot_name = f"{self._config.source_dataset}@{self._config.snapshot_prefix}_{timestamp}"
        backup_dir = Path(self._config.backup_directory)
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_file = backup_dir / f"{self._config.snapshot_prefix}_{timestamp}.zfs"

        self._zfs_ops.create_snapshot(snapshot_name)
        self._zfs_ops.send_to_file(snapshot_name, backup_file)

        if not backup_file.exists():
            raise BackupError(f"Backup file was not created: {backup_file}")
        if backup_file.stat().st_size <= 0:
            raise BackupError(f"Backup file is empty: {backup_file}")

        try:
            retention = apply_retention(
                backup_dir,
                snapshot_prefix=self._config.snapshot_prefix,
                keep=self._config.max_backups,
            )
        except RetentionError as exc:
            raise BackupError(str(exc)) from exc

        return BackupResult(
            snapshot_name=snapshot_name,
            backup_file=backup_file,
            deleted_backups=retention.deleted_backups,
            source_snapshot_cleanup="kept",
        )
