zum Report: [Report Abgabe 1 ](report/report.md)

## Anleitung zur Ausführung des Codes im Ordner `05 Pipe`

### 1. **Wechsle in das Hauptverzeichnis**

Navigiere in das Hauptverzeichnis des Projekts:

```bash
cd /home/marvin/Desktop/Uni-Trier/2025WEdition/05\ Pipe
```

---

### 2. **Baue das Projekt**

Verwende den `Makefile`, um das Projekt zu kompilieren:

```bash
make
```

---

### 3. **Wechsle in das `bin`-Verzeichnis**

Nach dem erfolgreichen Kompilieren findest du die ausführbaren Dateien im `bin`-Ordner. Wechsle in dieses Verzeichnis:

```bash
cd bin
```

---

### 4. **Führe die Programme aus**

Im `bin`-Ordner findest du die ausführbaren Dateien `pipe` und `ipc_pipe`. Du kannst sie wie folgt ausführen:

```bash
./pipe
```

oder

```bash
./ipc_pipe
```

---

### 5. **Generiere die Plots**

Um die Plots zu generieren, navigiere in den `plots`-Ordner und führe das Python-Skript aus:

```bash

cd ../plots
# Gegebenenfalls erst mit requirements.txt venv erstellen
python create_plots.py --csv ../pipe.csv --outdir ./output
python create_plots.py --csv ../ipc_pipe.csv --outdir ./output_ipc
```

Die generierten Plots werden im Ordner `./output` gespeichert.
