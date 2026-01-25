import zmq
import time
import random
import os
import socket as py_socket


def run_actor():
    role = os.getenv("ROLE") #aus docker-compose-file
    my_id = py_socket.gethostname() #hostname des containers (eg c4000ced8d66)

    ctx = zmq.Context()
    socket = ctx.socket(zmq.DEALER) #sendet an ROUTER (office)
    socket.setsockopt(zmq.IDENTITY, my_id.encode()) #.encode() wichtig - umwandlung string in bytes b'...'
    socket.connect("tcp://office:5555")

    while True:
        #random sleep
        wait = random.uniform(5, 15) if role == "reindeer" else random.uniform(2, 6)
        time.sleep(wait)

        # send an office
        socket.send_json({"role": role})

        # warten (echtes schlafen) auf Antwort. Anders als erste Version mit REQ-Socket
        socket.recv_json()
        print(f"{'🫎' if role == 'reindeer' else random.choice(['🧝‍♂️', '🧝‍♀️', '🧝'])} {role.capitalize()} {my_id}: Freigabe erhalten!", flush=True)

        # sleep für Schlitten ziehen oder Hilfe bekommen
        time.sleep(2)


if __name__ == "__main__":
    run_actor()
