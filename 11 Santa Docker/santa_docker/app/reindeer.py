import os, random, zmq, time
from datetime import datetime
from config import *

def run_reindeer():
    name = os.getenv("REINDEER_NAME", "Unbekannt")
    context = get_zmq_context()
    sub = context.socket(zmq.SUB); sub.connect(f"tcp://{SANTA_HOST}:{PUB_PORT}"); sub.subscribe("")
    push = context.socket(zmq.PUSH); push.connect(f"tcp://{SANTA_HOST}:{PUSH_PORT}")

    at_north_pole = False
    has_delivered = False

    while True:
        msg = sub.recv_string()
        if msg.startswith("TIME:"):
            dt = datetime.strptime(msg.split(":")[1], "%Y-%m-%d")
            date_str = dt.strftime("%d.%m.")
            day, month = dt.day, dt.month

            if month == 1 and day == 1: has_delivered = False

            if not at_north_pole and not has_delivered:
                if month < 12 or (month == 12 and day <= 15):
                    pass
                elif month == 12 and day >= 16:
                    prob = (2 ** (day - 16)) / 100.0
                    if random.random() < prob or day == 24:
                        at_north_pole = True
                        print(f"{CLR_TIME}[{date_str}]{CLR_RESET} {CLR_REINDEER}[{name}]: Bin zurück am Nordpol!{CLR_RESET}")
                        push.send_string(f"REINDEER_ARRIVAL:{name}")

            elif at_north_pole and has_delivered:
                if month == 12 and day >= 25:
                    prob = (2 ** (day - 25)) / 100.0
                    if random.random() < prob or day == 31:
                        at_north_pole = False
                        print(f"{CLR_TIME}[{date_str}]{CLR_RESET} {CLR_REINDEER}[{name}]: Tschüss! Ab in den Süden.{CLR_RESET}")

        elif msg == "EVENT:FLY_AWAY":
            if at_north_pole:
                has_delivered = True
                print(f"{CLR_REINDEER}[{name}]: Schlittenfahrt war super! Jetzt kurz ausruhen.{CLR_RESET}")

if __name__ == "__main__":
    time.sleep(2)
    run_reindeer()