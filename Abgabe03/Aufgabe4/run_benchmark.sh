#!/bin/bash

TEST_DIR=$1

# Prüfen, ob ein Pfad übergeben wurde
if [ -z "$TEST_DIR" ]; then
    echo "Fehler: Bitte das Testverzeichnis angeben!"
    echo "Nutzung: ./run_benchmark.sh /pfad/zum/ordner"
    exit 1
fi

echo "=================================================="
echo " Dateisystem Benchmark gestartet auf: $TEST_DIR "
echo "=================================================="

echo -e "\n[ Test 1: Sequentielles Schreiben ]"
echo "-> Fokus: Durchsatz / Bandbreite (Simuliert große Dateien)"
sudo fio --name=seq_write --rw=write --bs=1M --size=1G --numjobs=1 --directory=$TEST_DIR | grep -E "WRITE:|iops|bw"

echo -e "\n[ Test 2: Random Read/Write ]"
echo "-> Fokus: IOPS (Simuliert Datenbanken & OS-Zugriffe mit 4KB Blöcken)"
sudo fio --name=rand_rw --rw=randrw --bs=4k --size=500M --numjobs=1 --directory=$TEST_DIR | grep -E "READ:|WRITE:|iops|bw"

echo -e "\n=================================================="
echo " Benchmark abgeschlossen! Bereit für die Dokumentation."