import time
import os

filepath = "/pool2/dauerlauf.txt"

print("Programm gestartet. Ich schreibe und lese jetzt ununterbrochen...")

try:
    i = 0
    while True:
        # Schreiben
        with open(filepath, "a") as f:
            f.write(f"Zeile {i}: System läuft stabil\n")
            f.flush()
            os.fsync(f.fileno())
        
        # Lesen (um Integrität zu prüfen)
        with open(filepath, "r") as f:
            content = f.readlines()[-1]
        
        print(f"Schreib/Lese-Test {i} erfolgreich: {content.strip()}")
        i += 1
        time.sleep(0.5)
except Exception as e:
    print(f"\nFEHLER AUFGETRETEN: {e}")