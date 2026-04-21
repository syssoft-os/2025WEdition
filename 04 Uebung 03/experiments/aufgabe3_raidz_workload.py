from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
import time


DEFAULT_TARGET = Path("/raidpool/data/workload.log")


def append_and_verify(*, target: Path, iteration: int) -> None:
    """Append one line, fsync it, then verify the line is readable again."""
    line = f"iteration={iteration} timestamp={datetime.now().isoformat()}"
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
        handle.flush()
        os.fsync(handle.fileno())

    content = target.read_text(encoding="utf-8")
    if line not in content:
        raise RuntimeError(f"verification failed: line not found after write: {line}")


def run_workload(*, target: Path, interval_seconds: float, max_iterations: int | None) -> None:
    """Run the simple read/write workload until interrupted or bounded completion."""
    iteration = 1
    try:
        while True:
            append_and_verify(target=target, iteration=iteration)
            print(f"iteration={iteration} ok")
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("stopped by user")


def build_parser() -> argparse.ArgumentParser:
    """Create the tiny CLI for the RAIDZ workload."""
    parser = argparse.ArgumentParser(
        description="Continuously write to and read from a RAIDZ-backed dataset."
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help=f"log file to use (default: {DEFAULT_TARGET})",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=1.0,
        help="sleep interval between iterations",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="optional upper bound for local sanity checks",
    )
    return parser


def main() -> int:
    """Parse arguments and run the workload."""
    args = build_parser().parse_args()
    run_workload(
        target=args.target,
        interval_seconds=args.interval_seconds,
        max_iterations=args.max_iterations,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
