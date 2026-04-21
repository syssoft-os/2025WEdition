import zmq
import os

# Konfiguration über Umgebungsvariablen
R_REQUIRED = int(os.getenv("R_COUNT", 9))
P_REQUIRED = int(os.getenv("P_COUNT", 3))

context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket.bind("tcp://*:5555")

waiting_reindeer = []  # Speichert Identitäten der Rentiere
waiting_elves = []  # Speichert Identitäten der Elfen

print(f"🎅 Santa-Zentrale gestartet (R={R_REQUIRED}, P={P_REQUIRED})...")

while True:
    # Nachricht empfangen: [Identität, leerer Frame, Inhalt]
    # print("🎅 Wartet auf Nachrichten...")
    identity, empty, message = socket.recv_multipart()
    msg_text = message.decode()

    if msg_text == "REINDEER_READY":
        waiting_reindeer.append(identity)
        print(
            f"🦌 Rentier gemeldet. Warteschlange: {len(waiting_reindeer)}/{R_REQUIRED}"
        )

    elif msg_text == "ELF_PROBLEM":
        waiting_elves.append(identity)
        print(f"🧝 Elf gemeldet. Warteschlange: {len(waiting_elves)}/{P_REQUIRED}")

    # Logik-Prüfung
    if len(waiting_reindeer) >= R_REQUIRED:
        print("🎅 Ho Ho Ho! Alle Rentiere da. Schlitten wird bereitgemacht!")
        for _ in range(R_REQUIRED):
            rid = waiting_reindeer.pop(0)
            socket.send_multipart([rid, b"", b"START_FLYING"])

    elif len(waiting_elves) >= P_REQUIRED:
        print(f"🎅 Santa hilft einer Gruppe von {P_REQUIRED} Elfen.")
        for _ in range(P_REQUIRED):
            eid = waiting_elves.pop(0)
            socket.send_multipart([eid, b"", b"PROBLEM_SOLVED"])
