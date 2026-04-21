import threading
import time
import random


ANZAHL_RENTIERE = 10                # Gesamtanzahl der Rentiere
ANZAHL_ELFEN = 15                   # Gesamtanzahl der Elfen
ELFEN_GRUPPE = 4                    # p: Anzahl der Elfen, die es benötigt, um den Weihnachtsmann zu wecken

elf_counter = 0                     # Zähler für die Anzahl der wartenden Elfen
reindeer_counter = 0                # Zähler für die Anzahl der zurückgekehrten Rentiere

counterMutex = threading.Semaphore(1)      # counterMutex: Schützt die Zähler (elf_counter, reindeer_count) so, dass nur ein Thread gleichzeitig darauf zugreifen kann
elfMutex = threading.Semaphore(1)   # Mutex, der sicherstellt, dass immer nur genau p Elfen den Weihnachtsmann blockieren

santaSem = threading.Semaphore(0)   # Semaphore, auf dem der Weihnachtsmann schläft
reindeerSem = threading.Semaphore(0)# Semaphore, auf dem die Rentiere warten, bis alle da sind
elfSem = threading.Semaphore(0)     # Semaphore, auf dem die Elfen warte, bis der Weihnachtsmann ihnen hilft


# Sorgt dafür, dass Ausgaben nicht vermischt werden
print_lock = threading.Semaphore(1)

def synchronized_print(msg):
    """Hilfsfunktion für saubere Ausgaben ohne Vermischung."""
    with print_lock:
        print(msg)


def santa():
    global reindeer_counter, elf_counter  # Zugriff auf die globalen Zähler
    synchronized_print("Der Weihnachtsmann schläft")

    while True:
        santaSem.acquire()          # Der Weihnachtsmann wartet darauf, geweckt zu werden

        counterMutex.acquire()             # Zugriff auf die Zähler

        # Abfragen, ob alle Rentiere zurück sind
        if reindeer_counter == ANZAHL_RENTIERE:
            synchronized_print("Alle Rentiere sind zurück. Schlitten kann abflugbereit gemacht werden")

            reindeer_counter = 0  # Zähler wird zurückgesetzt
            counterMutex.release()  # Der Zugriff auf die Zähler wir wieder freigegeben

            synchronized_print("Der Schlitten ist abflugbereit und die Geschenke werden ausgeliefert")
            time.sleep(8)  # Simulation der Auslieferung für 8 Sekunden
            synchronized_print(
                "Der Weihnachtsmann ist zurück vom Ausliefern der Geschenke. Die Rentiere können wieder in den Süden fliegen. Der Weihnachtsmann schläft wieder.")

            for _ in range(ANZAHL_RENTIERE):
                reindeerSem.release()  # Alle Rentiere werden nacheinander in zufälliger Reihenfolge freigegeben


        # Abfragen, ob genug Elfen auf Hilfe warten
        elif elf_counter == ELFEN_GRUPPE:
            synchronized_print(f"{ELFEN_GRUPPE} Elfen brauchen Hilfe vom Weihnachtsmann.")

            counterMutex.release()  # Der Zugriff auf die Zähler wir wieder freigegeben

            synchronized_print(f"Der Weihnachtsmann hilft den {ELFEN_GRUPPE} Elfen")

            for _ in range(ELFEN_GRUPPE):
                time.sleep(2)     # Simulation der Hilfe für jede Elf (2 Sekunden)
                elfSem.release()    # Die 4 wartenden Elfen werden nacheinander in zufälliger Reihenfolge freigegeben
            synchronized_print("Allen Elfen wurde geholfen. Der Weihnachtsmann schläft wieder.")


        else:
            # Es sind weder genung Rentiere da, noch benötigen genug Elfen Hilfe
            counterMutex.release()         # Der Zugriff auf die Zähler wird wieder freigegeben


def reindeer(id):
    global reindeer_counter

    while True:
        # Rentiere sind für eine zufällige Zeit im Süden im Urlaub
        time.sleep(random.randint(15, 40))   # Urlaubsdauer zwischen 2 und 15 Sekunden (gleichmäßig verteilt)

        counterMutex.acquire()             # Zugriff auf die Zähler
        reindeer_counter += 1          # Ein weiters Rentier ist zurückgekehrt
        synchronized_print(f"Rentier {id} ist zurück am Nordpol ({reindeer_counter}/{ANZAHL_RENTIERE})")

        if reindeer_counter == ANZAHL_RENTIERE:
            santaSem.release()      # Das letzte Rentier weckt den Weihnachtsmann auf

        counterMutex.release()             # Der Zugriff auf die Zähler wir wieder freigegeben

        reindeerSem.acquire()      # Rentier wartet solange, bis alle Rentiere da sind und der Weihnachtsmann den Schlitten abflugbereit macht


def elf(id):
    global elf_counter

    while True:
        time.sleep(random.randint(5, 20))   # Zeit, die eine Elf arbeitet, bevor es ein Problem hat

        elfMutex.acquire()          # Sicherstellen, dass nur genau p Elfen den Weihnachtsmann blockieren
        counterMutex.acquire()             # Zugriff auf die Zähler

        elf_counter += 1            # Eine weitere Elf benötigt Hilfe
        synchronized_print(f"Elf {id} benötigt Hilfe ({elf_counter}/{ELFEN_GRUPPE})")

        if elf_counter == ELFEN_GRUPPE:
            santaSem.release()      # Genug Elfen haben ein Problem und wecken den Weihnachtsmann auf
            # elfMutex wird erst wieder freigegeben, wenn der Weihnachtsmann den Elfen geholfen hat

        else:
            elfMutex.release()      # Wenn nicht genug Elfen da sind, wird der elfMutex wieder freigegeben, sodass weitere Elfen dazukommen können

        counterMutex.release()             # Der Zugriff auf die Zähler wir wieder freigegeben

        elfSem.acquire()            # Die Elfen warten, bis der Weihnachtsmann ihnen geholfen hat

        counterMutex.acquire()             # Zugriff auf die Zähler
        elf_counter -= 1            # Dem Elf wurde geholfen

        if elf_counter == 0:
            elfMutex.release()      # Wenn allen Elfen geholfen wurde, wird der elfMutex wieder freigegeben

        counterMutex.release()             # Der Zugriff auf die Zähler wir wieder freigegeben


threads = []                        # Liste aller Threads

# Erstellen des Weihnachtsmann-Threads
santa_thread = threading.Thread(target=santa, daemon=True)   # Thread für den Weihnachtsmann, der die Funktion santa() ausführt
santa_thread.start()                # Starten des Weihnachtsmann-Threads
threads.append(santa_thread)        # Hinzufügen des Weihnachtsmann-Threads zur Liste der Threads

# Erstellen der Rentier-Threads
for i in range(ANZAHL_RENTIERE):
    t = threading.Thread(target=reindeer, args=(i + 1,), daemon=True)  # Thread für ein Rentier mit id i+1, der die Funktion reindeer() ausführt
    t.start()                       # Starten des Rentier-Threads
    threads.append(t)               # Hinzufügen des Rentier-Threads zur Liste der Threads

# Erstellen der Elfen-Threads
for i in range(ANZAHL_ELFEN):
    t = threading.Thread(target=elf, args=(i + 1,), daemon=True)       # Thread für eine Elf mit id i+1, der die Funktion elf() ausführt
    t.start()                       # Starten des Elf-Threads
    threads.append(t)               # Hinzufügen des Elf-Threads zur Liste der Threads

try:
    for t in threads:
        t.join()                    # Warten auf das Ende aller Threads (in diesem Fall läuft das Programm unendlich)
except KeyboardInterrupt:
    synchronized_print("Programm wird beendet.")






