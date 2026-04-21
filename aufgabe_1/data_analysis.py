import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import sys
import os

def analyze_latency_data(csv_path):
    
    """
    Load CSV file and calculate statistics for latency measurements.

    input:
        csv_path: path to csv file containing measurements
    returns
        dictionary with statistics and DataFrame

    remark:
        DataFrame contains: 'mean', 'meadian', 'std', 'min', 'max', 'ci_lower', 
                            'ci_upper', 'p50', 'p95', 'p99', 'items'
    """

    df = pd.read_csv(csv_path, header=None, names=['measurements'])

    # Subtract 50,000 from all measurements
    df['measurements'] = df['measurements'] - 50000
    
    # statistics
    mean = df['measurements'].mean()
    median = df['measurements'].median()
    std = df['measurements'].std()
    min_val = df['measurements'].min()
    max_val = df['measurements'].max()

    confidence = 0.95
    n = len(df)
    stderr = stats.sem(df['measurements'])
    ci = stderr * stats.t.ppf((1 + confidence) / 2, n-1)

    # calculate percentiles
    p50 = df['measurements'].quantile(0.50)
    p95 = df['measurements'].quantile(0.95)
    p99 = df['measurements'].quantile(0.99)

    stats_dict = {
        'mean': mean,
        'median': median,
        'std': std,
        'min': min_val,
        'max': max_val,
        'ci_lower': mean - ci,
        'ci_upper': mean + ci,
        'p50': p50,
        'p95': p95,
        'p99': p99,
        'items': n
    }

    return stats_dict, df

def plot_distribution(df, title='Latency'):
    """
    Create a visualisation of the input data

    input:
        df: DataFrame with 'measurements' colum 
        title: plot title
    """

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Histogram
    p995 = df['measurements'].quantile(0.995)
    df_filtered = df[df['measurements'] <= p995]

    axes[0, 0].hist(df_filtered['measurements'], bins=50, edgecolor='black', alpha=0.7)
    axes[0, 0].set_xlabel('Latency (ns)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title(f'Histogram (99.5% of data, n={len(df_filtered):,})')
    axes[0, 0].grid(True, alpha=0.3)

    # outlier info
    outliers = len(df) - len(df_filtered)
    axes[0, 0].text(0.95, 0.95, f'{outliers:,} outliers removed\nMax: {df["measurements"].max():.0f}ns', 
                    transform=axes[0, 0].transAxes, 
                    verticalalignment='top', horizontalalignment='right',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))


    # Time series
    if len(df) > 10000:
        df_sampled = df.iloc[::len(df)//10000]  # Sample ~10k points
    else:
        df_sampled = df
    
    axes[0, 1].plot(df_sampled.index, df_sampled['measurements'], linewidth=0.5, alpha=0.7)
    axes[0, 1].set_xlabel('Iteration')
    axes[0, 1].set_ylabel('Latency (ns)')
    axes[0, 1].set_title('Time Series (sampled)')
    axes[0, 1].set_ylim(df['measurements'].quantile(0.001), df['measurements'].quantile(0.999))  # Clip to 99.8% range
    axes[0, 1].grid(True, alpha=0.3)
    
    # Box plot
    axes[1, 0].boxplot(df_filtered['measurements'], vert=True)
    axes[1, 0].set_ylabel('Latency (ns)')
    axes[1, 0].set_title('Box Plot (outliers removed)')
    axes[1, 0].grid(True, alpha=0.3)
    
    # CDF
    sorted_data = np.sort(df['measurements'])
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    axes[1, 1].plot(sorted_data, cdf, linewidth=2)
    axes[1, 1].set_xlabel('Latency (ns)')
    axes[1, 1].set_ylabel('CDF')
    axes[1, 1].set_title('Cumulative Distribution')
    axes[1, 1].set_xlim(df['measurements'].quantile(0.001), df['measurements'].quantile(0.999))  # Focus on main range
    axes[1, 1].grid(True, alpha=0.3)
    
    # percentile lines
    for percentile, label in [(0.5, 'P50'), (0.95, 'P95'), (0.99, 'P99')]:
        val = df['measurements'].quantile(percentile)
        axes[1, 1].axhline(y=percentile, color='r', linestyle='--', alpha=0.5, linewidth=1)
        axes[1, 1].axvline(x=val, color='r', linestyle='--', alpha=0.5, linewidth=1)
        axes[1, 1].text(val, percentile, f' {label}={val:.0f}ns', fontsize=8)
    
    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    return fig

def print_statistics(stats_dict, name=''):
    """Print formatted statistics."""
    print(f"\n{'='*60}")
    print(f"Statistics for {name}")
    print(f"{'='*60}")
    print(f"Count:              {stats_dict['items']:,}")
    print(f"Mean:               {stats_dict['mean']:.2f} ns")
    print(f"Median:             {stats_dict['median']:.2f} ns")
    print(f"Std Deviation:      {stats_dict['std']:.2f} ns")
    print(f"Min:                {stats_dict['min']:.2f} ns")
    print(f"Max:                {stats_dict['max']:.2f} ns")
    print(f"95% CI:             [{stats_dict['ci_lower']:.2f}, {stats_dict['ci_upper']:.2f}] ns")
    print(f"50th Percentile:    {stats_dict['p50']:.2f} ns")
    print(f"95th Percentile:    {stats_dict['p95']:.2f} ns")
    print(f"99th Percentile:    {stats_dict['p99']:.2f} ns")
    print(f"{'='*60}\n")

if __name__ == '__main__':

    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python data_analysis.py <csv_file> [output_name]")
        print("\nExample:")
        print("  python data_analysis.py output/semaphore.csv")
        print("  python data_analysis.py output/filesystem_read.csv filesystem_read")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found")
        sys.exit(1)
    
    # Extract name from filename or use provided name
    if len(sys.argv) >= 3:
        name = sys.argv[2]
    else:
        # Extract name from path: output/semaphore.csv -> semaphore
        name = os.path.splitext(os.path.basename(csv_file))[0]
    
    # Generate output filename
    output_file = f"analysis/{name}.png"
    
    # Create analysis directory if it doesn't exist
    os.makedirs("analysis", exist_ok=True)
    
    # Run analysis
    stats, df = analyze_latency_data(csv_file)
    print_statistics(stats, name)
    plot_distribution(df, f"{name.replace('_', ' ').title()} Latency")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_file}")
    plt.show()