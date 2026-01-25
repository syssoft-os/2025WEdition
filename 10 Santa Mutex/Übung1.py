import threading
import time
import random
from datetime import datetime, timedelta

# --- Konfiguration ---
NUM_ELVES = 15
NUM_REINDEER = 9
ELVES_NEEDED = 5
P_ELF_PROBLEM = 0.05
REINDEER_NAMES = ["Dasher", "Dancer", "Prancer", "Vixen", "Comet", "Cupid", "Donner", "Blitzen", "Rudolph"]

# --- ANSI Farben ---
CLR_SANTA = "\033[91m"     # Rot
CLR_ELF = "\033[92m"       # Grün
CLR_REINDEER = "\033[94m"  # Blau
CLR_TIME = "\033[93m"      # Gelb
CLR_RESET = "\033[0m"

# --- Synchronisation ---
santa_sem = threading.Semaphore(0)
mutex = threading.Semaphore(1)
elf_sem = threading.Semaphore(0)
reindeer_sem = threading.Semaphore(0)

elf_count = 0
reindeer_count = 0
simulation_running = True
current_date = datetime(2025, 11, 1) 

def log(color, entity, message):
    timestamp = current_date.strftime("%d.%m.")
    print(f"{CLR_TIME}[{timestamp}]{CLR_RESET} {color}[{entity}]: {message}{CLR_RESET}")

# --- Rollen ---

def santa():
    global elf_count, reindeer_count
    log(CLR_SANTA, "Santa", "Entspannung im Hauptquartier.")
    while simulation_running:
        santa_sem.acquire()
        
        with mutex:
            if reindeer_count == NUM_REINDEER:
                log(CLR_SANTA, "Santa", "Ho Ho Ho! Alle Rentiere sind da. Abflug!")
                reindeer_count = 0
                for _ in range(NUM_REINDEER):
                    reindeer_sem.release()
                time.sleep(0.1)
            
            elif elf_count >= ELVES_NEEDED:
                log(CLR_SANTA, "Santa", f"Hilft einer Gruppe von {ELVES_NEEDED} Elfen.")
                for _ in range(ELVES_NEEDED):
                    elf_sem.release()
                elf_count -= ELVES_NEEDED

def elf(elf_id):
    global elf_count
    name = f"Elf {elf_id:02d}"
    while simulation_running:
        time.sleep(1)
        
        # Betriebsferien vom 24.12. bis 01.01.
        if (current_date.month == 12 and current_date.day >= 24) or (current_date.month == 1 and current_date.day == 1):
            continue

        if random.random() < P_ELF_PROBLEM:
            log(CLR_ELF, name, "Ich habe ein Problem!")
            with mutex:
                elf_count += 1
                if elf_count == ELVES_NEEDED:
                    santa_sem.release()
            
            elf_sem.acquire()
            log(CLR_ELF, name, "Problem gelöst!")

def reindeer(name):
    global reindeer_count
    while simulation_running:
        at_north_pole = False
        while not at_north_pole:
            time.sleep(1)
            
            if current_date.month == 12 and current_date.day >= 15:
                days_since_16 = (current_date.day - 16)
                prob = (2 ** days_since_16) / 100.0
                
                if random.random() < prob:
                    log(CLR_REINDEER, name, "Bin zurück am Nordpol!")
                    at_north_pole = True
                    with mutex:
                        reindeer_count += 1
                        if reindeer_count == NUM_REINDEER:
                            santa_sem.release()
        
        reindeer_sem.acquire()
        log(CLR_REINDEER, name, "Schlittenfahrt war super! Jetzt kurz ausruhen.")

        flying_home = False
        while not flying_home:
            time.sleep(1)
            if current_date.month == 12 and current_date.day >= 25:
                days_since_25 = (current_date.day - 25)
                prob = (2 ** days_since_25) / 100.0
                if random.random() < prob or current_date.day == 31:
                    log(CLR_REINDEER, name, "Tschüss! Ab in den Süden.")
                    flying_home = True
        
        while current_date.month == 12:
            time.sleep(1)

# --- Main (Zeitsteuerung) ---

if __name__ == "__main__":
    t_santa = threading.Thread(target=santa, daemon=True)
    t_santa.start()
    
    for i in range(1, NUM_ELVES + 1):
        threading.Thread(target=elf, args=(i,), daemon=True).start()
        
    for r_name in REINDEER_NAMES:
        threading.Thread(target=reindeer, args=(r_name,), daemon=True).start()

    try:
        print(f"{CLR_TIME}Simulation gestartet (1s = 1 Tag).{CLR_RESET}")
        while True:
            time.sleep(1)
            current_date += timedelta(days=1)
            
            if current_date.day == 1:
                print(f"\n{CLR_TIME}--- {current_date.strftime('%B %Y')} ---{CLR_RESET}\n")
            
            if current_date.month == 12 and current_date.day == 24:
                 with mutex:
                     if reindeer_count < NUM_REINDEER:
                         pass 
    except KeyboardInterrupt:
        print("\nSimulation beendet.")