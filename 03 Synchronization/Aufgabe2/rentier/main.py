import zmq
import time
import argparse
import random

def main():
    # Lesen der ID des Rentiers aus den Argumenten
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, required=True)
    args = parser.parse_args()
    my_id = f"Rentier-{args.id}"

    # Erstellen eines ZMQ Kontexts, um mit dem Weihnachtsmann zu kommunizieren
    context = zmq.Context()

    # Erstellen eines DEALER Sockets und Verbinden mit dem Santa Socket auf Port 5555
    socket = context.socket(zmq.DEALER)
    socket.setsockopt(zmq.IDENTITY, my_id.encode('utf-8'))
    socket.connect("tcp://santa:5555")

    while True:
        # Simuliere die Zeit im Süden
        vacation_time = random.uniform(10,50)
        time.sleep(vacation_time)

        # Ankunft am Nordpol, informiere den Weihnachtsmann
        socket.send_string("I_AM_HERE")

        while True:
            # Warten auf eine Nachricht vom Weihnachtsmann (blockiert bis eine Nachricht eintrifft)
            msg = socket.recv()
            command = msg.decode('utf-8')

            if command == "FLY_SOUTH":
                break  # Weihnachten vorbei, innere Schleife verlassen, wieder Urlaub machen


if __name__ == "__main__":
    main()