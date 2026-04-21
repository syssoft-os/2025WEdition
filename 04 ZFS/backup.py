import os
import sys
import subprocess
from datetime import datetime

# --- KONFIGURATION ---
DATASET_X = "pool1/daten_x"        # ZFS Dataset
BACKUP_DIR_Y = os.path.expanduser("~/zfs_backups") # Zielordner im Home Verzeichnis
MAX_BACKUPS = 3                    # Anzahl Sicherungen
RESTORE_TARGET = "pool1/daten_x_restore" 
# -------------------------------------

def run_command(cmd):
    """Führt einen Befehl aus und zeigt Fehler an"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FEHLER: {result.stderr}")
    return result

def main():
    # Restore-Aufruf 
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        all_backups = sorted([f for f in os.listdir(BACKUP_DIR_Y) if f.endswith(".zfs")])
        if all_backups:
            latest_backup = os.path.join(BACKUP_DIR_Y, all_backups[-1])
            print(f"--- Führe Restore mit 'zfs receive' durch ---")
            print(f"Stelle {latest_backup} nach {RESTORE_TARGET} wieder her...")
            run_command(f"sudo zfs receive {RESTORE_TARGET} < {latest_backup}")
            print("--- Restore abgeschlossen ---\n")
        return
    # ------------------------------------------------------------------

    # 1. Zielordner Y erstellen, falls er nicht existiert
    if not os.path.exists(BACKUP_DIR_Y):
        os.makedirs(BACKUP_DIR_Y)
        print(f"Ordner {BACKUP_DIR_Y} wurde erstellt.")

    # 2. Namen für Snapshot und Datei generieren
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snap_name = f"{DATASET_X}@{timestamp}"
    backup_file = os.path.join(BACKUP_DIR_Y, f"backup_{timestamp}.zfs")

    print(f"\n--- Starte Backup: {timestamp} ---")

    # 3. ZFS Snapshot erstellen
    print(f"Erstelle Snapshot: {snap_name}")
    run_command(f"sudo zfs snapshot -r {snap_name}") 

    # 4. ZFS Send nutzen
    print(f"Sende Snapshot in Datei: {backup_file}")
    # Wir leiten den Stream mit '>' in eine Datei um
    run_command(f"sudo zfs send -R {snap_name} > {backup_file}") 

    # 5. Retention-Verfahren (Alte Kopien löschen)
    # Liste alle .zfs Dateien im Ordner Y auf, sortiert nach Name
    all_backups = sorted([f for f in os.listdir(BACKUP_DIR_Y) if f.endswith(".zfs")])
    
    if len(all_backups) > MAX_BACKUPS:
        # Berechne wie viele gelöscht werden müssen
        to_delete = all_backups[:-MAX_BACKUPS] # Alle außer den neuesten N
        for old_file in to_delete:
            file_path = os.path.join(BACKUP_DIR_Y, old_file)
            print(f"Retention: Lösche altes Backup {old_file}")
            os.remove(file_path)

    print("--- Backup abgeschlossen ---\n")

if __name__ == "__main__":
    main()