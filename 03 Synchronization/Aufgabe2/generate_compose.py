# Konfiguration: Wie viele Container sollen erstellt werden
NUM_ELVES = 15
NUM_REINDEER = 10

compose_header = """services:
  santa:
    build: .
    container_name: santa
    command: python -u santa/main.py
    networks:
      - northpole_net
    ports:
      - "5555:5555"
"""

compose_network = """
networks:
  northpole_net:
    driver: bridge
"""

with open("docker-compose.yml", "w") as f:
    f.write(compose_header)

    # Elfen generieren
    for i in range(1, NUM_ELVES + 1):
        entry = f"""
  elf{i}:
    build: .
    container_name: elf{i}
    command: python -u elf/main.py --id {i}
    depends_on:
      - santa
    networks:
      - northpole_net
"""
        f.write(entry)

    # Rentiere generieren
    for i in range(1, NUM_REINDEER + 1):
        entry = f"""
  rentier{i}:
    build: .
    container_name: rentier{i}
    command: python -u rentier/main.py --id {i}
    depends_on:
      - santa
    networks:
      - northpole_net
"""
        f.write(entry)

    f.write(compose_network)

print(f"docker-compose.yml wurde generiert mit {NUM_ELVES} Elfen und {NUM_REINDEER} Rentieren.")