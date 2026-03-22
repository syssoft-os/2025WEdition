from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import time


DEFAULT_TARGET = Path("/sourcepool/data/live_transaction.log")


def build_phase_one_record(*, tx_id: int, payload: str) -> str:
    """Return the first half of a logical record without its commit marker."""
    checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"tx={tx_id} payload={payload} checksum={checksum} "


def write_in_two_phases(*, target: Path, tx_id: int, payload: str, window_seconds: float) -> None:
    """Write a logical record, pause mid-write, then finish it later."""
    target.parent.mkdir(parents=True, exist_ok=True)
    first_half = build_phase_one_record(tx_id=tx_id, payload=payload)

    with target.open("w", encoding="utf-8") as handle:
        handle.write(first_half)
        handle.flush()
        os.fsync(handle.fileno())

        print(f"TARGET: {target}")
        print(f"PHASE 1 WRITTEN: {first_half!r}")
        print(f"WINDOW OPEN: start backup now (sleeping {window_seconds:g}s)")
        time.sleep(window_seconds)

        handle.write("COMMIT\n")
        handle.flush()
        os.fsync(handle.fileno())

    print("WRITE COMPLETE")


def build_parser() -> argparse.ArgumentParser:
    """Create the tiny CLI for the inconsistency experiment."""
    parser = argparse.ArgumentParser(
        description="Write one logical record in two phases so a ZFS backup can capture an incomplete state."
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help=f"file to write (default: {DEFAULT_TARGET})",
    )
    parser.add_argument(
        "--tx-id",
        type=int,
        default=1,
        help="transaction identifier written into the record",
    )
    parser.add_argument(
        "--payload",
        default="100",
        help="payload value to embed in the record",
    )
    parser.add_argument(
        "--window-seconds",
        type=float,
        default=10.0,
        help="how long the inconsistency window stays open before COMMIT is appended",
    )
    return parser


def main() -> int:
    """Run the two-phase writer experiment."""
    args = build_parser().parse_args()
    write_in_two_phases(
        target=args.target,
        tx_id=args.tx_id,
        payload=args.payload,
        window_seconds=args.window_seconds,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
