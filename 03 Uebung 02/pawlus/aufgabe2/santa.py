import zmq
import time


def santa():
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REP)
    socket.bind("tcp://*:5556")

    print("🎅 Santa: Ich schlafe...", flush=True)

    while True:
        task = socket.recv_json()
        #print(task)
        role = task.get("role")

        if role == "reindeer":
            print("🎅 Santa: Wuahhh, schon wieder Weihnachten! Schlitten bereit machen!", flush=True)
            time.sleep(2)
        else:
            print("🎅 Santa: Ich helfe den Elfen bei den Geschenken.", flush=True)
            time.sleep(1)

        socket.send_json({"status": "finished"})


if __name__ == "__main__":
    santa()
