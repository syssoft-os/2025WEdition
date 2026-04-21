import time
from datetime import datetime, timedelta
import zmq
from config import *

def run_santa():
    context = get_zmq_context()
    pub = context.socket(zmq.PUB)
    pub.bind(f"tcp://*:{PUB_PORT}")
    
    pull = context.socket(zmq.PULL)
    pull.bind(f"tcp://*:{PUSH_PORT}")
    pull.setsockopt(zmq.RCVTIMEO, 200)

    current_date = datetime(2025, 11, 1)
    elf_queue = []
    reindeer_ready = []

    print(f"{CLR_SANTA}[Santa]: Entspannung im Hauptquartier{CLR_RESET}")

    while True:
        date_iso = current_date.strftime("%Y-%m-%d")
        date_pretty = current_date.strftime("%d.%m.")
        pub.send_string(f"TIME:{date_iso}")
        
        while True:
            try:
                msg = pull.recv_string()
                if msg.startswith("ELF_PROBLEM"):
                    eid = msg.split(":")[1]
                    if eid not in elf_queue: elf_queue.append(eid)
                elif msg.startswith("REINDEER_ARRIVAL"):
                    rid = msg.split(":")[1]
                    if rid not in reindeer_ready: reindeer_ready.append(rid)
            except zmq.Again:
                break

        if len(reindeer_ready) == NUM_REINDEER:
            if current_date.month == 12 and current_date.day == 24:
                print(f"{CLR_TIME}[{date_pretty}]{CLR_RESET} {CLR_SANTA}[Santa]: Ho Ho Ho! Alle Rentiere sind da. Abflug!{CLR_RESET}")
                pub.send_string("EVENT:FLY_AWAY")
                reindeer_ready = []
        
        elif len(elf_queue) >= ELVES_NEEDED:
            helping = elf_queue[:ELVES_NEEDED]
            print(f"{CLR_TIME}[{date_pretty}]{CLR_RESET} {CLR_SANTA}[Santa]: Hilft Gruppe: {helping}{CLR_RESET}")
            pub.send_string(f"EVENT:HELP_ELVES:{','.join(helping)}")
            elf_queue = elf_queue[ELVES_NEEDED:]

        current_date += timedelta(days=1)
        time.sleep(1)

if __name__ == "__main__":
    run_santa()