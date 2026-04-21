import polars as pl
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent

df_linux = pl.read_csv(BASE_DIR / "results" / "results_linux_stopwatch.csv")
df_linux_nocache = pl.read_csv(BASE_DIR / "results" / "results_linux_stopwatch_nocache.csv")
df_wsl = pl.read_csv(BASE_DIR / "results" / "results_wsl_stopwatch.csv")
df_wsl_nocache = pl.read_csv(BASE_DIR / "results" / "results_wsl_stopwatch_nocache.csv")

syscalls = ["open", "write", "read", "close"]




# === STATISTIKEN ===

def generic_stats(df, syscalls):
    for col in syscalls:
        d = df[col]
        mean, std = d.mean(), d.std()
        ci = 1.96 * std / np.sqrt(len(d))
        print(f"{col.upper()}: Mean={mean:.2f}μs, Min={d.min():.2f}μs, Max={d.max():.2f}μs, StdDev={std:.2f}μs, 95%CI=[{mean-ci:.2f},{mean+ci:.2f}]μs")
    print("")

generic_stats(df_linux, syscalls)
generic_stats(df_linux_nocache, syscalls)
generic_stats(df_wsl, syscalls)
generic_stats(df_wsl_nocache, syscalls)


# graph linux chached vs wsl cached
linux_cached = [124.88, 5.70, 0.86, 12.76]
linux_nocache = [32.19, 7.85, 2.03, 20.12]
wsl_cached = [899.07, 121.73, 102.42, 206.69]
wsl_nocache = [1177.64, 136.96, 105.30, 218.29]

x = range(len(syscalls))

plt.figure(figsize=(8, 5))
width = 0.4
bars_linux = plt.bar([i - width/2 for i in x], linux_cached, width=width, label="Linux Native")
bars_wsl = plt.bar([i + width/2 for i in x], wsl_cached, width=width, label="WSL Mount")

plt.xticks(x, syscalls)
plt.ylabel("Zeit (µs)")
plt.title("Vergleich: Linux Native vs WSL Mount (Cached)")
plt.legend()

# Werte über Balken
for bar in bars_linux:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height, f"{height:.1f}", 
             ha="center", va="bottom")

for bar in bars_wsl:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height, f"{height:.1f}", 
             ha="center", va="bottom")

plt.tight_layout()
plt.savefig(BASE_DIR / "images/linux_native_vs_wsl_mount_cached.png")



#graph: wsl mount cached vs notchached
x = range(len(syscalls))
bw = 0.4

plt.figure(figsize=(8, 5))

bars_cached = plt.bar([i - bw/2 for i in x], wsl_cached, width=bw, label="WSL Mount (Cached)")
bars_nocache = plt.bar([i + bw/2 for i in x], wsl_nocache, width=bw, label="WSL Mount (No-Cache)")

plt.xticks(x, syscalls)
plt.ylabel("Zeit (µs)")
plt.title("WSL Mount – Cached vs No-Cache")
plt.legend()

# Werte über Balken
for bar in bars_cached:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, h, f"{h:.1f}",
             ha="center", va="bottom")

for bar in bars_nocache:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, h, f"{h:.1f}",
             ha="center", va="bottom")

plt.tight_layout()
plt.savefig(BASE_DIR / "images/wsl_mount_cached_vs_wsl_mount_nocache.png")






# abb linux cached vs no-cached
x = range(len(syscalls))
bw = 0.4

plt.figure(figsize=(8, 5))

bars_cached = plt.bar([i - bw/2 for i in x], linux_cached, width=bw, label="Linux Native (Cached)")
bars_nocache = plt.bar([i + bw/2 for i in x], linux_nocache, width=bw, label="Linux Native (No-Cache)")

plt.xticks(x, syscalls)
plt.ylabel("Zeit (µs)")
plt.title("Linux Native – Cached vs No-Cache")
plt.legend()

# Werte über Balken
for bar in bars_cached:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, h, f"{h:.2f}",
             ha="center", va="bottom")

for bar in bars_nocache:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, h, f"{h:.2f}",
             ha="center", va="bottom")

plt.tight_layout()
plt.savefig(BASE_DIR / "images/linux_native_cached_vs_linux_native_nocache.png")
