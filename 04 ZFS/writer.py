import time
import os

filepath = "/pool1/daten_x/transaktion.txt"

print("Programm gestartet. Schreiben des Anfangs")
with open(filepath, "w") as f:
    f.write("--- TRANSAKTION START ---\n")
    f.flush() # Erzwingt das Schreiben auf die virtuelle Platte
    os.fsync(f.fileno()) # Stellt sicher, dass es im Dateisystem ankommt

print("Anfang geschrieben. Warten für 20 Sekunden. Jetzt Snapshot machen")
time.sleep(20)

with open(filepath, "a") as f:
    f.write("--- TRANSAKTION ENDE ---\n")
    f.flush()
    os.fsync(f.fileno())

print("Ende geschrieben. Vorgang abgeschlossen.")