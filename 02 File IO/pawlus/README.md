**Franz Pawlus (1422169) — Betriebssysteme (Übung 1)**
---

## **1. Projektübersicht**
Dieses Projekt misst die Latenzen der vier Datei-System-Calls: 
**Open – Read – Write – Close (ORWC)**
unter zwei Einflussfaktoren:
1. **Caching**
   – Linux Page Cache aktiv vs. per `drop_caches` deaktiviert
2. **Virtualisierungsschicht in WSL2**
   – Native Linux-Dateien (ext4)
   – NTFS-Mount unter `/mnt/c/...` (9P-Protokoll → VM-Grenze)

Die Messungen werden in `.csv` gespeichert und anschließend durch 
ein ein Python-Skript statistisch ausgewertet.

---

## **2. Verzeichnisstruktur**

```
2025WEdition/
└── 02 File IO/
    └── pawlus/
        ├── orwc_cached_stopwatch.cpp
        ├── orwc_nocache_stopwatch.cpp
        ├── analyze.py
        ├── pyproject.toml
        ├── results/   # erzeugte CSVs
        └── images/    # erzeugte Diagramme
```

---

## 3. Voraussetzungen und Abhängigkeiten

Um die Ergebnisse zu reproduzieren, wird eine Linux-Umgebung (z.B. Ubuntu 24.04 unter WSL2) benötigt.

**Software:**
*   **C++ Compiler:** `g++` (oder kompatibel) mit C++11 Support.
*   **Helper-Library:** Die im Vorlesungs-Repository bereitgestellte `stopwatch`-Klasse muss kompiliert und gelinkt werden.
*   **Python 3.10+:** Für die Auswertung.
*   **Python-Bibliotheken:** `polars`, `numpy`, `matplotlib`.

## 4. Durchführung der Messungen

### Kompilierung
Die C++ Programme müssen unter Einbindung der `Helper`-Library (Header und Static Lib) kompiliert werden.

### Ausführungshinweise
Um die im Bericht diskutierten Effekte zu reproduzieren, ist der Ausführungsort entscheidend:

1.  **Szenario "Linux Native":** Das kompilierte Programm muss zwingend im **nativen Linux-Dateisystem** (z.B. im Home-Verzeichnis `~`) liegen und dort ausgeführt werden, um den Overhead des Windows-Dateisystems zu vermeiden.
2.  **Szenario "WSL Mount":** Das Programm wird direkt im **gemounteten Windows-Verzeichnis** (z.B. `/mnt/c/...`) ausgeführt.
3.  **Root-Rechte:** Die `nocache`-Variante benötigt Root-Rechte (`sudo`), um den Befehl zum Leeren des Page Cache an den Kernel senden zu können.

## 5. Auswertung

Das Skript `analyze.py` liest die vier CSV-Dateien aus dem Ordner `results/` ein. Es berechnet die statistischen Kennzahlen, gibt diese auf der Konsole aus und speichert die Vergleichsdiagramme im Ordner `images/`.