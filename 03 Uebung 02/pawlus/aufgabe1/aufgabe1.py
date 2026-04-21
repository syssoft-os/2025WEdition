import threading
import time
import random

NUM_REINDEER = 9  # r
NUM_ELVES = 10  # e
ELF_GROUP_SIZE = 3  # p


# Mutex: Schützt Status-Variablen (reindeer_count, elf_count) vor Race Conditions.
mutex = threading.Semaphore(1)

# intial == 0, damit bei santaSem.acquire() Santa erstmal schläft defaultmäßig
santaSem = threading.Semaphore(0)

# Rentiere warten hier auf Santa
reindeerSem = threading.Semaphore(0)

# Elfen warten hier auf Hilfe von Santa
elfSem = threading.Semaphore(0)

# #stellt sicher, dass keine neue Elfen ankommen, solange Santa hilft/Geschenke verteilt -> ansonsten Racecondition santa vs elves -> Deadlock
elfTex = threading.Semaphore(1)

reindeer_count = 0
elf_count = 0


def santa():
    global reindeer_count, elf_count
    print("🎅 Santa: Ich lege mich schlafen...")
    while True:
        santaSem.acquire()  # Warten, bis jemand Santa weckt

        with mutex:
            # Alle Rentiere sind da
            if reindeer_count == NUM_REINDEER:
                print("🎅 Santa: Alle Rentiere da! Mach den Schlitten bereit!")
                for _ in range(NUM_REINDEER):
                    reindeerSem.release()
                reindeer_count = 0
                time.sleep(1)  # Simulation der Auslieferung
                print("🎅 Santa: Auslieferung fertig. Ich geh wieder schlafen.")

            # Gruppe Elfen braucht Hilfe
            elif elf_count == ELF_GROUP_SIZE:
                print("🎅 Santa: Ich helfe jetzt der Elfengruppe...")
                for _ in range(ELF_GROUP_SIZE):
                    elfSem.release()
                time.sleep(0.5) # Santa hilft
                print("🎅 Santa: Elfen geholfen. Zurück in den Schlaf.")


def reindeer(id):
    global reindeer_count
    while True:
        # Rentiere im Urlaub
        time.sleep(random.uniform(5, 10))

        with mutex:
            reindeer_count += 1
            print(
                f"🦌 Rentier {id}: Bin zurück am Nordpol ({reindeer_count}/{NUM_REINDEER})"
            )
            if reindeer_count == NUM_REINDEER:
                santaSem.release()  # letzte Rentier weckt Santa

        reindeerSem.acquire()  # Warten, bis Santa sie anspannt
        print(f"🦌 Rentier {id}: Ich fliege den Schlitten!")
        time.sleep(0.1)  # Fliegen...


def elf(id):
    global elf_count
    while True:
        # Elfen arbeiten an Geschenken
        time.sleep(random.uniform(2, 6))


        elfTex.acquire() # verhindert Überlauf der Zählervariable -> deadlock wenn elf_count > 3 ansonsten
        with mutex:
            elf_count += 1
            print(f"🧝 Elf {id}: Ich habe ein Problem ({elf_count}/{ELF_GROUP_SIZE})")
            if elf_count == ELF_GROUP_SIZE:
                santaSem.release()  # Der dritte Elf weckt Santa
            else:
                elfTex.release()

        elfSem.acquire()  # Warten auf Hilfe
        print(f"🧝 Elf {id}: Santa hat mir geholfen.")

        with mutex:
            elf_count -= 1
            if elf_count == 0:
                # Der letzte Elf der Gruppe gibt den Zugang für die nächsten Elfen frei
                elfTex.release()

        print(f"🧝 Elf {id}: Gehe wieder Geschenke bauen.")


if __name__ == "__main__":
    t_santa = threading.Thread(target=santa, daemon=True)
    t_santa.start()

    for i in range(NUM_REINDEER):
        t = threading.Thread(target=reindeer, args=(i + 1,), daemon=True)
        t.start()

    for i in range(NUM_ELVES):
        t = threading.Thread(target=elf, args=(i + 1,), daemon=True)
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n--- Simulation beendet ---")
