import threading
import time
import random

# --- Konfiguration ---
R = 9  # Anzahl der Rentiere [cite: 10]
E = 10  # Gesamtzahl der Elfen [cite: 10]
P = 3  # Anzahl der Elfen, die den Weihnachtsmann wecken

# --- Semaphore & Zähler ---
# Der Weihnachtsmann wartet hier (Initial 0 = blockiert)
santa_sem = threading.Semaphore(0)
# Rentiere warten hier auf das Anspannen des Schlittens
reindeer_sem = threading.Semaphore(0)
# Elfen warten hier auf die Hilfe des Weihnachtsmanns
elf_sem = threading.Semaphore(0)
# Mutex zum Schutz der Zähler (Mutual Exclusion)
mutex = threading.Semaphore(1)

reindeer_count = 0
elf_count = 0


def santa():
    global reindeer_count, elf_count
    print("🎅 Weihnachtsmann: Ich schlafe und sammle Kraft...")

    while True:
        santa_sem.acquire()  # Warten, bis er geweckt wird

        mutex.acquire()
        # Priorität 1: Rentiere (Schlitten bereitmachen)
        if reindeer_count == R:
            print(
                "🎅 Weihnachtsmann: Alle Rentiere sind da! Ich bereite den Schlitten vor."
            )
            for _ in range(R):
                reindeer_sem.release()
            reindeer_count = 0
            print("🎅 Weihnachtsmann: Ho Ho Ho! Geschenke werden ausgeliefert!")

        # Priorität 2: Elfen (Probleme bei der Produktion)
        elif elf_count == P:
            print(f"🎅 Weihnachtsmann: Ich helfe den {P} Elfen bei ihren Fragen.")
            for _ in range(P):
                elf_sem.release()
            elf_count = 0
            # Nach der Hilfe arbeitet Santa weiter/erholt sich

        mutex.release()


def reindeer(id):
    global reindeer_count
    while True:
        # Rentiere entspannen sich im Süden
        time.sleep(random.uniform(8, 10))

        mutex.acquire()
        reindeer_count += 1
        print(f"🦌 Rentier {id}: Ich bin zurück am Nordpol ({reindeer_count}/{R}).")

        if reindeer_count == R:
            santa_sem.release()  # Das letzte Rentier weckt Santa
        mutex.release()

        reindeer_sem.acquire()  # Warten, bis Santa den Schlitten anspannt
        print(f"🦌 Rentier {id}: Ich ziehe jetzt den Schlitten!")
        time.sleep(2)  # Simulation der Auslieferung


def elf(id):
    global elf_count
    while True:
        # Elfen arbeiten an Geschenken
        time.sleep(random.uniform(1, 5))

        mutex.acquire()
        if elf_count < P:
            elf_count += 1
            print(f"🧝 Elf {id}: Ich habe ein Problem ({elf_count}/{P}).")

            if elf_count == P:
                santa_sem.release()  # Der dritte Elf weckt Santa
            mutex.release()

            elf_sem.acquire()  # Warten auf Hilfe vom Weihnachtsmann
            print(f"🧝 Elf {id}: Danke für die Hilfe, Santa! Ich arbeite weiter.")
        else:
            # Falls schon P Elfen warten, muss dieser Elf später wiederkommen
            mutex.release()


# --- Programmstart ---
if __name__ == "__main__":
    # 1. Weihnachtsmann Thread
    threading.Thread(target=santa, daemon=True).start()

    # 2. Rentier Threads
    for i in range(R):
        threading.Thread(target=reindeer, args=(i,), daemon=True).start()

    # 3. Elfen Threads
    for i in range(E):
        threading.Thread(target=elf, args=(i,), daemon=True).start()

    # Simulation für eine gewisse Zeit laufen lassen
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSimulation beendet.")
