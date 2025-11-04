import pandas as pd
import matplotlib.pyplot as plt
import argparse

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('filename', type=str, help='the csv filename to plot')
args = parser.parse_args()

df = pd.read_csv(args.filename)
ax = df.plot(style='-', linewidth=1.5, figsize=(10, 6))
ax.set_title('ORWC Benchmark Results', fontsize=14, fontweight='bold', pad=15)
ax.grid(True, axis='y', linestyle='--', alpha=0.5)
ax.set_xlabel('Iteration', fontsize=11)
ax.set_ylabel('Time (ms)', fontsize=11)
plt.tight_layout()
plt.savefig('plot.png', dpi=150)
plt.show()
print(f"Plot saved to {args.filename}.png")