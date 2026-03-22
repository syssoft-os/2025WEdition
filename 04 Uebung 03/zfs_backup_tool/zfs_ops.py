from __future__ import annotations

from pathlib import Path
import subprocess


class ZfsCommandError(RuntimeError):
    """Raised when a ZFS command fails."""


class ZfsOps:
    """Small command adapter around the required ZFS operations."""

    @staticmethod
    def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
        """Run a subprocess command without shell interpolation."""
        try:
            return subprocess.run(
                cmd,
                check=True,
                shell=False,
                capture_output=kwargs.pop("capture_output", False),
                text=kwargs.pop("text", False),
                **kwargs,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else exc.stderr
            detail = stderr.strip() if stderr else str(exc)
            raise ZfsCommandError(detail) from exc

    def dataset_exists(self, dataset: str) -> bool:
        """Return True if the dataset exists, otherwise False."""
        try:
            self._run(["zfs", "list", dataset], capture_output=True, text=True)
        except ZfsCommandError:
            return False
        return True

    def create_snapshot(self, snapshot_name: str) -> None:
        """Create a ZFS snapshot."""
        self._run(["zfs", "snapshot", snapshot_name])

    def send_to_file(self, snapshot_name: str, target_path: str | Path) -> None:
        """Write a snapshot stream into a .zfs file."""
        target = Path(target_path)
        with target.open("wb") as handle:
            self._run(["zfs", "send", snapshot_name], stdout=handle)

    def receive_from_file(self, backup_file: str | Path, restore_dataset: str) -> None:
        """Replay a .zfs file into a restore dataset using zfs receive."""
        source = Path(backup_file)
        with source.open("rb") as handle:
            self._run(["zfs", "receive", restore_dataset], stdin=handle)
