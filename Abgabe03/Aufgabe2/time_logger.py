import time
from datetime import datetime

file_path = "/backuppool/dataset/uhrzeit.txt"
print(f"Schreibe Sekunden-Log in {file_path}...")

with open(file_path, "w") as f:
    while True:
        aktuelle_zeit = datetime.now().strftime("%H:%M:%S")

        # Teil 1: Zeilenanfang schreiben und sofort auf die Platte zwingen
        f.write(f"Uhrzeit: {aktuelle_zeit} - [Snapshot-Fenster offen]... ")
        f.flush()

        time.sleep(2)

        # Teil 2: Zeile beenden
        f.write("Zeile komplett!\n")
        f.flush()
