#!/usr/bin/env python3
"""Create a time-series plot and histograms for a CSV with two columns: iteration and latency.

This script uses a constant for the default CSV filename (one level up: `pipe.csv`).
You can override the CSV path with --csv. Plots are saved as PNG files next to this script by default.

### Features:
1. **Time-Series Plot**:
   - Visualizes latency over iterations.

2. **Main Histogram**:
   - Focuses on the main range of latency values (up to the 99th percentile).
   - Displays the percentage of data points covered in the visible range.

3. **Outliers Histogram**:
   - Focuses on the outliers (latency values above the 99th percentile).
   - Displays the percentage of data points covered in the visible range.

### Arguments:
- `--csv` or `-c`: Path to the input CSV file (default: `../pipe.csv`).
- `--outdir` or `-o`: Directory to save the generated plots (default: the script folder).
"""

from pathlib import Path
import argparse
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# Constant for the CSV filename: default is ../pipe.csv (one level up from plots/)
DEFAULT_CSV = Path(__file__).resolve().parent.parent / "pipe.csv"


def load_csv(path: Path) -> pd.DataFrame:
    """Load CSV and ensure it has iteration and latency columns.

    - If the CSV has headers, it checks for 'iteration' and 'latency' columns.
    - If no headers are present, it assumes the first two columns are 'iteration' and 'latency'.
    """
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    df = pd.read_csv(path)
    if df.shape[1] >= 2:
        cols = [c.lower() for c in df.columns]
        if "iteration" in cols and "latency" in cols:
            df.columns = cols
            return pd.DataFrame(df[["iteration", "latency"]])
        else:
            df = pd.read_csv(path, header=None, names=["iteration", "latency"])
            return pd.DataFrame(df)
    else:
        df = pd.read_csv(path, header=None, names=["iteration", "latency"])
        return pd.DataFrame(df)


def sanitize(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce columns to numeric and drop invalid rows.

    - Ensures 'iteration' and 'latency' columns are numeric.
    - Drops rows with invalid or missing values.
    """
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    required_columns = ["iteration", "latency"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df = pd.DataFrame(df[required_columns])  # Explicitly cast to DataFrame
    df["iteration"] = pd.to_numeric(df["iteration"], errors="coerce")
    df["latency"] = pd.to_numeric(df["latency"], errors="coerce")
    df = df.dropna().reset_index(drop=True)
    return df


def plot_time_series(df: pd.DataFrame, outpath: Path):
    """Generate a time-series plot of latency over iterations."""
    plt.figure(figsize=(10, 4))
    sns.lineplot(data=df, x="iteration", y="latency")
    plt.xlabel(f"Iteration (n = {len(df)})")
    plt.ylabel("Latency in µs")
    plt.title("Latency over Iterations")
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()


def plot_main_histogram(df: pd.DataFrame, outpath: Path):
    """Generate a histogram for the main range of latency values.

    - Focuses on values up to the 99th percentile.
    - Displays the percentage of data points covered in the visible range.
    """
    plt.figure(figsize=(8, 6))

    xlim_low = df["latency"].min()
    xlim_high = np.percentile(df["latency"], 99)
    bins = 100

    # Define bins for the histogram
    bins = np.linspace(xlim_low, xlim_high, bins + 1)

    # Create the histogram
    plt.hist(
        df["latency"], bins=bins.tolist(), color="skyblue", edgecolor="black", alpha=0.7
    )

    total_points = len(df)
    covered_points = df[
        (df["latency"] >= xlim_low) & (df["latency"] <= xlim_high)
    ].shape[0]
    coverage_percentage = (covered_points / total_points) * 100

    plt.xlim(xlim_low, xlim_high)

    # Add axis labels and title
    plt.xlabel("Latency in µs")
    plt.ylabel("Frequency")
    plt.title(
        f"Dieses Histogramm deckt {coverage_percentage:.2f}% aller Punkte ab. (n = {len(df)})"
    )
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)

    plt.close()


def plot_ouliers_histogram(df: pd.DataFrame, outpath: Path):
    """Generate a histogram for latency outliers.

    - Focuses on values above the 99th percentile.
    - Displays the percentage of data points covered in the visible range.
    """
    plt.figure(figsize=(8, 6))

    xlim_low = np.percentile(df["latency"], 99)
    xlim_high = df["latency"].max()
    bins = 100

    # Define bins for the histogram
    bins = np.linspace(xlim_low, xlim_high, bins + 1)

    # Create the histogram
    plt.hist(
        df["latency"], bins=bins.tolist(), color="skyblue", edgecolor="black", alpha=0.7
    )

    total_points = len(df)
    covered_points = df[
        (df["latency"] >= xlim_low) & (df["latency"] <= xlim_high)
    ].shape[0]
    coverage_percentage = (covered_points / total_points) * 100

    plt.xlim(xlim_low, xlim_high)

    # Add axis labels and title
    plt.xlabel("Latency in µs")
    plt.ylabel("Frequency")
    plt.title(
        f"Dieses Histogramm deckt {coverage_percentage:.2f}% aller Punkte ab. (n = {len(df)})"
    )
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)

    plt.close()


def main():
    """Main function to parse arguments and generate plots."""
    parser = argparse.ArgumentParser(
        description="Create time series plot and histograms for latency CSV."
    )
    parser.add_argument(
        "--csv",
        "-c",
        type=str,
        default=str(DEFAULT_CSV),
        help=f"Path to CSV file (default: {DEFAULT_CSV})",
    )
    parser.add_argument(
        "--outdir",
        "-o",
        type=str,
        default=str(Path(__file__).resolve().parent),
        help="Directory to save plots (default: the script folder)",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    try:
        df = load_csv(csv_path)
    except Exception as e:
        print("Failed to read CSV:", e)
        sys.exit(2)

    df = sanitize(df)
    if df.empty:
        print("No valid rows after parsing. Exiting.")
        sys.exit(3)

    plot_time_series(df, outdir / "latency_timeseries.png")
    plot_main_histogram(df, outdir / "latency_main_histogram.png")
    plot_ouliers_histogram(df, outdir / "latency_outliers_histogram.png")

    print("mean: ", df["latency"].mean())
    print("median: ", df["latency"].median())
    print("std: ", df["latency"].std())
    print("min: ", df["latency"].min())
    print("max: ", df["latency"].max())
    print("95th percentile: ", np.percentile(df["latency"], 95))
    print("99th percentile: ", np.percentile(df["latency"], 99))
    print("99.9th percentile: ", np.percentile(df["latency"], 99.9))


if __name__ == "__main__":
    main()
