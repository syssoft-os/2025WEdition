import zmq
import time
import argparse
import random

def main():
    # Lesen der ID des Elfen aus den Argumenten
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, required=True)
    args = parser.parse_args()
    my_id = f"Elf-{args.id}"

    # Erstellen eines ZMQ Kontexts, um mit dem Weihnachtsmann zu kommunizieren
    context = zmq.Context()

    # Erstellen eines DEALER Sockets und Verbinden mit dem Santa Socket auf Port 5555
    socket = context.socket(zmq.DEALER)
    socket.setsockopt(zmq.IDENTITY, my_id.encode('utf-8'))
    socket.connect("tcp://santa:5555")

    while True:
        # Simulation der Zeit bis ein Problem auftritt
        time_till_problem = random.uniform(5,30)
        time.sleep(time_till_problem)

        # Das Problem ist aufgetreten, Elf benötigt Hilfe und informiert den Weihnachtsmann
        socket.send_string("I_NEED_HELP")

        # Der Elf wartet, bis er eine Anweisung vom Weihnachtsmann erhält
        while True:
            # Warten auf eine Nachricht vom Weihnachtsmann (blockiert bis eine Nachricht eintrifft)
            msg = socket.recv()
            command = msg.decode('utf-8')

            if command == "BACK_WORK":
                break  # Dem Elfen wurde geholfen, er kann wieder arbeiten, also verlässt er die innere Schleife

if __name__ == "__main__":
    main()
