#!/usr/bin/env python3
"""
ZFS Backup and Archive Tool
===========================
This program implements a simple backup and archiving solution using ZFS snapshots.
It uses the Copy-on-Write technique with ZFS snapshots and the send/receive functions.

Requirements:
- ZFS utilities installed (zfs, zpool)
- Python 3.6+

Usage:
    python3 zfs_backup.py [--config CONFIG_FILE]

Configuration (config.json):
{
    "source_dataset": "pool/dataset",      # ZFS dataset to backup
    "backup_location": "/backup/path",      # Where to store backups
    "max_backups": 5,                       # Maximum number of backups to keep
    "snapshot_prefix": "backup_",           # Prefix for snapshot names
    "pool_name": "backuppool"               # ZFS pool name
}
"""

import json
import os
import subprocess
import sys
import argparse
from datetime import datetime
from pathlib import Path


class ZFSBackupTool:
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.source_dataset = self.config.get("source_dataset", "pool/source")
        self.backup_location = Path(self.config.get("backup_location", "/backup"))
        self.max_backups = self.config.get("max_backups", 5)
        self.snapshot_prefix = self.config.get("snapshot_prefix", "backup_")
        self.pool_name = self.config.get("pool_name", "backuppool")

    def load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {config_path} not found. Using defaults.")
            return {}

    def run_command(
        self, cmd: list, capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a shell command and return the result."""
        print(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd, capture_output=capture_output, text=True, check=True
            )
            if result.stdout:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")
            if e.stderr:
                print(f"stderr: {e.stderr}")
            raise

    def create_snapshot(self) -> str:
        """Create a ZFS snapshot of the source dataset."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"{self.snapshot_prefix}{timestamp}"
        full_snapshot = f"{self.source_dataset}@{snapshot_name}"

        print(f"Creating snapshot: {full_snapshot}")
        self.run_command(["zfs", "snapshot", full_snapshot])

        return snapshot_name

    def send_snapshot(self, snapshot_name: str) -> Path:
        """Send a ZFS snapshot to a backup file."""
        full_snapshot = f"{self.source_dataset}@{snapshot_name}"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_location / f"backup_{timestamp}.zfs"

        self.backup_location.mkdir(parents=True, exist_ok=True)

        print(f"Sending snapshot {full_snapshot} to {backup_file}")
        with open(backup_file, "wb") as f:
            # Wir nutzen subprocess.run direkt, um stdout in die Datei umzuleiten
            subprocess.run(["zfs", "send", "-c", full_snapshot], stdout=f, check=True)

        return backup_file

    def list_backups(self) -> list:
        """List all existing backup files."""
        if not self.backup_location.exists():
            return []

        backups = sorted(self.backup_location.glob("backup_*.zfs"))
        return backups

    def apply_retention(self):
        """Apply retention policy: delete oldest backups if max is exceeded."""
        backups = self.list_backups()

        if len(backups) > self.max_backups:
            num_to_delete = len(backups) - self.max_backups
            print(f"Retention: Deleting {num_to_delete} oldest backup(s)")

            for backup in backups[:num_to_delete]:
                print(f"Deleting old backup: {backup}")
                backup.unlink()

    def cleanup_snapshot(self, snapshot_name: str):
        """Remove a ZFS snapshot after successful backup."""
        full_snapshot = f"{self.source_dataset}@{snapshot_name}"
        print(f"Cleaning up snapshot: {full_snapshot}")
        try:
            self.run_command(["zfs", "destroy", full_snapshot])
        except subprocess.CalledProcessError:
            print(f"Warning: Could not destroy snapshot {full_snapshot}")

    def backup(self):
        """Perform a complete backup operation."""
        print("=" * 50)
        print("Starting ZFS Backup")
        print("=" * 50)

        try:
            snapshot_name = self.create_snapshot()
            backup_file = self.send_snapshot(snapshot_name)
            self.apply_retention()
            self.cleanup_snapshot(snapshot_name)

            print("=" * 50)
            print(f"Backup completed successfully!")
            print(f"Backup file: {backup_file}")
            print(f"Total backups: {len(self.list_backups())}")
            print("=" * 50)

        except Exception as e:
            print(f"Backup failed: {e}")
            sys.exit(1)

    def restore(self, backup_file: str):
        """Restore a backup from a ZFS snapshot file."""
        print(f"Restoring from: {backup_file}")

        with open(backup_file, "rb") as f:
            # Wir leiten die Datei als stdin in den receive-Befehl
            subprocess.run(
                ["zfs", "receive", "-F", self.source_dataset], stdin=f, check=True
            )

    def list_snapshots(self):
        """List all snapshots of the source dataset."""
        try:
            result = self.run_command(
                ["zfs", "list", "-t", "snapshot", "-r", self.source_dataset]
            )
            print("Existing snapshots:")
            print(result.stdout)
        except subprocess.CalledProcessError:
            print("No snapshots found or ZFS not available.")

    def status(self):
        """Show backup status and configuration."""
        print("ZFS Backup Tool Status")
        print("=" * 40)
        print(f"Source Dataset: {self.source_dataset}")
        print(f"Backup Location: {self.backup_location}")
        print(f"Max Backups: {self.max_backups}")
        print(f"Snapshot Prefix: {self.snapshot_prefix}")
        print(f"Pool Name: {self.pool_name}")
        print()

        backups = self.list_backups()
        print(f"Current Backups: {len(backups)}")
        for b in backups:
            size = b.stat().st_size
            print(f"  - {b.name} ({size / 1024 / 1024:.2f} MB)")

        print()
        self.list_snapshots()


def create_sample_config():
    """Create a sample configuration file."""
    config = {
        "source_dataset": "backuppool/dataset",
        "backup_location": "/backup",
        "max_backups": 5,
        "snapshot_prefix": "backup_",
        "pool_name": "backuppool",
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    print("Created sample config.json")
    return config


def main():
    parser = argparse.ArgumentParser(description="ZFS Backup and Archive Tool")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    parser.add_argument(
        "--create-config", action="store_true", help="Create sample config"
    )
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--restore", metavar="FILE", help="Restore from backup file")
    parser.add_argument("--list-snapshots", action="store_true", help="List snapshots")

    args = parser.parse_args()

    if args.create_config:
        create_sample_config()
        return

    tool = ZFSBackupTool(args.config)

    if args.status:
        tool.status()
    elif args.restore:
        tool.restore(args.restore)
    elif args.list_snapshots:
        tool.list_snapshots()
    else:
        tool.backup()


if __name__ == "__main__":
    main()
