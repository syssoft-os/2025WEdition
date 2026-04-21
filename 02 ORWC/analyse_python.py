# ORWC Latenz Analyse für Windows
# Dieses Skript analysiert die Latenzzeiten von Dateioperationen (open, write, read, close)
# und erstellt statistische Auswertungen sowie Visualisierungen.
#
# Matthias Simon, 1658438

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

# 1. Daten laden
filename = 'orwc_latencies_windows.csv'

try:
    df = pd.read_csv(filename)
except FileNotFoundError:
    print(f"Fehler: Die Datei '{filename}' wurde nicht gefunden.")
    exit(1)

# 2. Statistische Auswertung
stats_dict = {
    'Operation': [], 'Mean': [], 'Median': [], 'Min': [], 'Max': [], 'StdDev': [], 'CI_95_Margin': []
}
cols = ['open_us', 'write_us', 'read_us', 'close_us']
labels = ['Open', 'Write', 'Read', 'Close']

for col in cols:
    data = df[col]
    mean = np.mean(data)
    median = np.median(data)
    std_dev = np.std(data, ddof=1)  # Stichprobenstandardabweichung
    sem = stats.sem(data)   # Standardfehler des Mittels
    # 95% Konfidenzintervall
    ci_margin = sem * stats.t.ppf((1 + 0.95) / 2., len(data)-1)
    
    stats_dict['Operation'].append(col)
    stats_dict['Mean'].append(mean)
    stats_dict['Median'].append(median)
    stats_dict['Min'].append(np.min(data))
    stats_dict['Max'].append(np.max(data))
    stats_dict['StdDev'].append(std_dev)
    stats_dict['CI_95_Margin'].append(ci_margin)

stats_df = pd.DataFrame(stats_dict)

print("=== Statistische Auswertung ===")
pd.set_option('display.float_format', '{:.2f}'.format)
print(stats_df)
print("\n")

# 3. Visualisierung

plt.style.use('ggplot')
fig = plt.figure(figsize=(16, 8))

gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1])

# --- Linke Seite: Boxplot (Logarithmische Skala) ---
ax_box = fig.add_subplot(gs[:, 0]) 
df[cols].plot(kind='box', ax=ax_box, patch_artist=True)
ax_box.set_title('Gesamtverteilung & Ausreißer (Log Scale)')
ax_box.set_ylabel('Zeit in Mikrosekunden')
ax_box.set_yscale('log')
ax_box.set_xticklabels(labels)

# --- Rechte Seite: Histogramme mit Zoom (0-97%), damit Ausreißer nicht dominieren ---
ax_hist_open  = fig.add_subplot(gs[0, 1])
ax_hist_write = fig.add_subplot(gs[0, 2])
ax_hist_read  = fig.add_subplot(gs[1, 1])
ax_hist_close = fig.add_subplot(gs[1, 2])

axes_hists = [ax_hist_open, ax_hist_write, ax_hist_read, ax_hist_close]
colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B3']

for i, col in enumerate(cols):
    ax = axes_hists[i]
    data = df[col]
    
    # 97. Perzentil Berechnung für den Zoom
    p97 = np.percentile(data, 97)
    
    # range=(min, p97)
    ax.hist(data, bins=30, range=(np.min(data), p97), color=colors[i], alpha=0.7, edgecolor='white')
    
    mean_val = stats_dict['Mean'][i]
    ax.axvline(mean_val, color='black', linestyle='dashed', linewidth=1.5, label=f'Mean: {mean_val:.1f}')
    
    ax.set_title(f'Histogramm: {labels[i]} (Zoom 0-97%)')
    ax.set_ylabel('Häufigkeit')
    ax.set_xlabel('µs')
    ax.legend(loc='upper right', fontsize='small')
    
    ax.grid(True, alpha=0.3)

plt.tight_layout()

# 4. Grafik speichern
output_filename = 'latenz_auswertung_hist.png'
plt.savefig(output_filename, dpi=300)
print(f"Grafik gespeichert als: {output_filename}")

plt.show()

# Für die ersten x Zeilen der CSV-Datei sollen die LAtenzwerte in einem Diagramm geplottet werden
# dargestellt werden, um den Verlauf der Latenzzeiten zu visualisieren. 

x = 250  # Anzahl der zu plottenden Zeilen

df_sample = df.head(x)
plt.figure(figsize=(12, 6))
for col, label in zip(cols, labels):
    plt.plot(df_sample.index, df_sample[col], marker='o', linestyle='-', label=label)
plt.title(f'Latenzzeiten der ersten {x} Operationen')
plt.xlabel('Iteration')
plt.ylabel('Zeit in Mikrosekunden')
plt.legend()
plt.grid(True, alpha=0.3)


output_filename_sample = f'latenz_auswertung_plot{x}.png'
plt.savefig(output_filename_sample, dpi=300)
print(f"Sample Grafik gespeichert als: {output_filename_sample}")

plt.show()

# Ende des Skripts