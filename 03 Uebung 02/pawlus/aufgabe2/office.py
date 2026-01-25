import zmq
import json
import time


def office():
    ctx = zmq.Context()

    #kommuniziert mit DEALER-Sockets (Elfen, Rentier)
    # vorher: REQ/REP-Pattern (polling, aktives warten),
    # jetzt: DEALER/ROUTER pattern entspricht sleep eines semaphores besser
    client_portal = ctx.socket(zmq.ROUTER)
    client_portal.bind("tcp://*:5555")

    queues = {"reindeer": [], "elf": []} #speichert eingehende Anfragen
    limits = {"reindeer": 9, "elf": 3} #limits der warteschlangen, zusätzliche Anfragen ggf gepuffert



    # REQ-Socket, weil santa ist exclusive ressource (kann nicht gleichzeitig fliegen und helfen),
    #   modelliert mutex aus aufgabe 1 - wartet auf antwort von REP-Socket (Santa)
    santa_link = ctx.socket(zmq.REQ)
    santa_link.connect("tcp://santa:5556")



    print("🏢 Office: Biep Biep Bieeeeeep! Koordination gestartet...", flush=True)

    while True:
        msg_parts = client_portal.recv_multipart()
        #print(msg_parts) #[b'86b92d1c4f54', b'{"role": "elf"}']
        identity = msg_parts[0]
        payload = msg_parts[1]

        msg = json.loads(payload)
        role = msg.get("role")

        if role in queues:
            if identity not in queues[role]:
                queues[role].append(identity)
                print(
                    f"🏢 Office: {role.capitalize()} {identity.decode()} registriert ({len(queues[role])}/{limits[role]})",
                    flush=True,
                )

            if len(queues[role]) == limits[role]: #wenn spezifisches limit erreicht wecke Santa
                print(f"📢 Office: Gruppe ({role}) voll. Wecke Santa...", flush=True)

                santa_link.send_json({"role": role}) # send und warte auf antwort von santa
                santa_link.recv()

                for client_id in queues[role]: #Rückmeldung an Rentiere oder Elfen
                    client_portal.send_multipart(
                        [client_id, json.dumps({"status": "done"}).encode()]
                    )

                queues[role] = []
                print(f"✨ Office: Gruppe ({role}) fertig.", flush=True)

                #for cleaner logging, weil manchmal kam Eingangsbestätigung eines Elfs/Rentiers vor dem obigen Print
                time.sleep(0.5)


if __name__ == "__main__":
    office()
