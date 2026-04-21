import zmq
import time

def main():
    print("Start")
    context = zmq.Context()             # ZMQ Kontext erstellen
    socket = context.socket(zmq.ROUTER) # ROUTER Socket erstellen
    socket.bind("tcp://*:5555")         # Socket an Port 5555 binden

    print("Santa: Ich warte auf Elfen und Rentiere")

    waiting_elves = []                  # Liste der wartenden Elfen
    arrived_reindeer = []               # Liste der angekommenen Rentiere

    elf_group_size = 4                  # p: Wie viele Elfen nötig sind, um Santa zu wecken
    total_reindeer = 10                 # r: Gesamtanzahl der Rentiere



    while True:
        try:
            # 1. Nachrichten empfangen
            # Beim ROUTER socket kommt die Nachricht in 2 Teilen: [sender_id, message_content]
            msg = socket.recv_multipart()

            sender_id = msg[0]                          # ID des Senders
            message_content = msg[1].decode('utf-8')    # Inhalt der Nachricht

            # 2. Wer ist der Absender?
            if message_content == "I_NEED_HELP":
                if sender_id not in waiting_elves:
                    waiting_elves.append(sender_id)
                    print(f"Elf {sender_id.decode('utf-8')} braucht Hilfe. Insgesamt wartende Elfen: {len(waiting_elves)}/{elf_group_size}")


            elif message_content == "I_AM_HERE":
                if sender_id not in arrived_reindeer:
                    arrived_reindeer.append(sender_id)
                    print(f"Rentier {sender_id.decode('utf-8')} ist zurück. Insgesamt zurückgekehrte Rentiere: {len(arrived_reindeer)}/{total_reindeer}")


            # Checke, ob alle Rentiere zurück sind
            if len(arrived_reindeer) >= total_reindeer:
                print("Alle Rentiere sind da. Schlitten kann abflugbereit gemacht werden.")

                for r_id in arrived_reindeer:
                    socket.send_multipart([r_id, b"DELIVERING_GIFTS"])

                time.sleep(10)  # Simuliere die Zeit, der Weihnachtsmann braucht, um Geschenke zu liefern

                for r_id in arrived_reindeer:
                    socket.send_multipart([r_id, b"FLY_SOUTH"])

                print("Geschenke wurden geliefert. Rentiere fliegen zurück in den Süden.")

                arrived_reindeer = []  # Liste der zurückgekehrten Rentiere zurücksetzen

            # Checke, ob genug Elfen da sind, denen geholfen werden muss
            elif len(waiting_elves) == elf_group_size:
                print("Genug Elfen sind da. Ich helfe ihnen jetzt.")

                # Allen wartenden Elfen antworten
                for elf_id in waiting_elves:
                    socket.send_multipart([elf_id, b"HELPING_YOU"])

                time.sleep(8)       # Simuliere die Zeit, die Santa braucht, um zu helfen

                for elf_id in waiting_elves:
                    socket.send_multipart([elf_id, b"BACK_WORK"])

                print("Allen Elfen wurde geholfen.")

                waiting_elves = []  # Liste der wartenden Elfen zurücksetzen


        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Santa: Error {e}")

if __name__ == "__main__":
    main()