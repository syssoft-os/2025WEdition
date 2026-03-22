from __future__ import annotations

import argparse
from pathlib import Path
import sys

from zfs_backup_tool.backup import BackupService
from zfs_backup_tool.config import ConfigError, load_config
from zfs_backup_tool.restore import RestoreService
from zfs_backup_tool.zfs_ops import ZfsOps


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for the MVP commands."""
    parser = argparse.ArgumentParser(prog="zfs-backup-tool")
    subparsers = parser.add_subparsers(dest="command")

    backup_parser = subparsers.add_parser("backup", help="run one backup pass")
    backup_parser.add_argument(
        "--config",
        required=True,
        help="path to the JSON configuration file",
    )

    restore_parser = subparsers.add_parser("restore", help="restore a .zfs backup file")
    restore_parser.add_argument(
        "--config",
        required=True,
        help="path to the JSON configuration file",
    )
    restore_parser.add_argument(
        "--backup-file",
        required=False,
        help="path to the .zfs file to restore",
    )

    return parser


def main(
    argv: list[str] | None = None,
    *,
    backup_service_cls=BackupService,
    restore_service_cls=RestoreService,
    zfs_ops_factory=ZfsOps,
) -> int:
    """Parse arguments and validate the config for MVP commands."""
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        return 0

    args = parser.parse_args(argv)

    if args.command in {"backup", "restore"}:
        try:
            config = load_config(Path(args.config))
        except ConfigError as exc:
            parser.exit(status=2, message=f"Configuration error: {exc}\n")
        if args.command == "backup":
            backup_service_cls(config=config, zfs_ops=zfs_ops_factory()).run()
        if args.command == "restore":
            if not args.backup_file:
                parser.exit(status=2, message="restore requires --backup-file\n")
            restore_service_cls(zfs_ops=zfs_ops_factory()).run(
                backup_file=Path(args.backup_file),
                restore_dataset=config.restore_dataset,
            )
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
