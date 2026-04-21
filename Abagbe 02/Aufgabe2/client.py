import zmq
import time
import random
import os

ROLE = os.getenv("ROLE", "ELF")  # "ELF" oder "REINDEER"
SANTA_HOST = os.getenv("SANTA_HOST", "santa")

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect(f"tcp://{SANTA_HOST}:5555")

while True:

    wait = random.uniform(2, 10)
    # print(f"{ROLE}: Warte {wait:.2f} Sekunden...")
    time.sleep(wait)  # Arbeitet oder entspannt im Süden

    msg = "ELF_PROBLEM" if ROLE == "ELF" else "REINDEER_READY"
    print(f"{ROLE}: Sende Status an Santa...")
    socket.send_string(msg)

    # Warten auf Antwort von Santa
    reply = socket.recv_string()
    print(f"{ROLE}: Erhaltene Antwort: {reply}")
