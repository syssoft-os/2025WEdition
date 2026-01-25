import os
import zmq
from datetime import datetime

NUM_ELVES = 15
NUM_REINDEER = 9
ELVES_NEEDED = 5
P_ELF_PROBLEM = 0.05  # P_e

# Netzwerk-Konfiguration
SANTA_HOST = os.getenv("SANTA_HOST", "santa")
PUB_PORT = 5555   # Santa -> Alle (Zeit & Events)
PUSH_PORT = 5556  # Akteure -> Santa (Meldungen)

# ANSI Farben
CLR_SANTA = "\033[91m"
CLR_ELF = "\033[92m"
CLR_REINDEER = "\033[94m"
CLR_TIME = "\033[0m"
CLR_RESET = "\033[0m"

def get_zmq_context():
    return zmq.Context()