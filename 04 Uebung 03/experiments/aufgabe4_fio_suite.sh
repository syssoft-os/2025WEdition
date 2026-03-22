#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 <label> <target_dir> <output_dir>" >&2
  echo "example: $0 zfs /benchpool/data /media/sf_bung03/artifacts/aufgabe4/run1_zfs" >&2
  exit 1
fi

label="$1"
target_dir="$2"
output_dir="$3"

mkdir -p "$output_dir"

seq_file="$target_dir/bench.bin"
rand_file="$target_dir/bench-rand.bin"

rm -f "$seq_file" "$rand_file"

run_fio() {
  local name="$1"
  shift

  fio \
    --name="$name" \
    --direct=1 \
    --numjobs=1 \
    --group_reporting=1 \
    "$@" \
    --output="$output_dir/$name.txt"
}

run_fio "${label}_seq_write" \
  --directory="$target_dir" \
  --filename="$seq_file" \
  --rw=write \
  --bs=1M \
  --size=1G

run_fio "${label}_seq_read" \
  --directory="$target_dir" \
  --filename="$seq_file" \
  --rw=read \
  --bs=1M \
  --size=1G

run_fio "${label}_randrw_4k" \
  --directory="$target_dir" \
  --filename="$rand_file" \
  --rw=randrw \
  --bs=4k \
  --size=512M

echo "benchmark suite complete for label=$label"
echo "results stored in $output_dir"
