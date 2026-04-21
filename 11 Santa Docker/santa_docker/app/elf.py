import os, random, zmq, socket
from datetime import datetime
from config import *

def run_elf():
    elf_id = os.getenv("ELF_ID", socket.gethostname()[-4:])
    context = get_zmq_context()
    sub = context.socket(zmq.SUB); sub.connect(f"tcp://{SANTA_HOST}:{PUB_PORT}"); sub.subscribe("")
    push = context.socket(zmq.PUSH); push.connect(f"tcp://{SANTA_HOST}:{PUSH_PORT}")

    has_problem = False
    
    while True:
        msg = sub.recv_string()
        if msg.startswith("TIME:"):
            dt = datetime.strptime(msg.split(":")[1], "%Y-%m-%d")
            date_str = dt.strftime("%d.%m.")

            is_holiday = (dt.month == 12 and dt.day >= 24) or (dt.month == 1 and dt.day == 1)
            
            if not has_problem and not is_holiday:
                if random.random() < P_ELF_PROBLEM:
                    has_problem = True
                    print(f"{CLR_TIME}[{date_str}]{CLR_RESET} {CLR_ELF}[Elf {elf_id}]: Ich habe ein Problem!{CLR_RESET}")
                    push.send_string(f"ELF_PROBLEM:{elf_id}")
        
        elif msg.startswith("EVENT:HELP_ELVES:"):
            if elf_id in msg.split(":")[2].split(","):
                has_problem = False
                print(f"{CLR_TIME}[{date_str}]{CLR_RESET} {CLR_ELF}[Elf {elf_id}]: Problem gelöst!{CLR_RESET}")

if __name__ == "__main__":
    run_elf()