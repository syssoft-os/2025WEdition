// orwc.c
// Misst die Latenzzeiten für Dateioperationen (open, write, read, close) unter Windows.
// Die Ergebnisse werden in eine CSV-Datei geschrieben, die später analysiert werden kann.
//
// Matthias Simon, 1658438

#include <windows.h>   // Windows-API: CreateFile, ReadFile, WriteFile, CloseHandle, etc.
#include <stdio.h>     // Standard-I/O: printf, FILE, fopen, fprintf, fclose
#include <stdlib.h>    // strtoull für Kommandozeilenargumente, exit
#include <stdint.h>    // Feste Ganzzahltypen wie uint64_t für Zeitmessung

// Hilfsfunktion: Berechnet die Frequenz des Performance-Counters in Hz.
// Die Frequenz wird nur einmal ermittelt und dann zwischengespeichert (static).
static inline uint64_t perf_freq_hz(void) {
    static uint64_t freq = 0;
    if (freq == 0) {
        LARGE_INTEGER f;
        QueryPerformanceFrequency(&f);
        freq = (uint64_t)f.QuadPart;
    }
    return freq;
}

// Hilfsfunktion: Gibt den aktuellen Zählerstand in Mikrosekunden zurück.
static inline uint64_t now_us(void) {
    LARGE_INTEGER c;
    QueryPerformanceCounter(&c);
    // Umrechnung auf Mikrosekunden: (Zählerstand * 1.000.000) / Frequenz
    return (uint64_t)((c.QuadPart * 1000000ULL) / perf_freq_hz());
}

int main(int argc, char **argv) {
    // Standardanzahl von Wiederholungen, falls kein Argument übergeben wird.
    size_t iterations = 100000;
    if (argc >= 2) {
        // Kommandozeilenargument auslesen, um die Anzahl der Iterationen festzulegen.
        iterations = (size_t)strtoull(argv[1], NULL, 10);
        if (iterations == 0) iterations = 100000;
    }

    // Pfad zur temporären Datei im aktuellen Arbeitsverzeichnis.
    const char *path = "orwc_temp_messung.tmp";
    // Pfad zur CSV-Ausgabedatei, in der die Rohdaten gespeichert werden.
    const char *csv_path = "orwc_latencies_windows.csv";

    // Schreibpuffer mit Teststring "test", der in die Datei geschrieben wird.
    const char wbuf[] = "test";
    const DWORD wlen = (DWORD)sizeof(wbuf);

    // CSV-Datei für die Ausgabe der Messergebnisse öffnen.
    FILE *csv_file = fopen(csv_path, "w");
    if (csv_file == NULL) {
        perror("Fehler beim Öffnen der CSV-Datei");
        return EXIT_FAILURE;
    }

    // Kopfzeile in die CSV-Datei schreiben
    fprintf(csv_file, "open_us,write_us,read_us,close_us\n");

    // "Warm-up": Temporäre Datei einmalig anlegen und wieder schließen.
    // Dies hilft, "Kaltstart"-Effekte des Dateisystems
    // aus der eigentlichen Messschleife herauszuhalten.

    HANDLE warmup = CreateFileA(path, GENERIC_READ | GENERIC_WRITE, 0, NULL,
                                   CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (warmup == INVALID_HANDLE_VALUE) {
        fprintf(stderr, "Fehler bei der Erstellung der temporären Datei.\n");
        fclose(csv_file);
        return EXIT_FAILURE;
    }
    CloseHandle(warmup);

    printf("Messung wird gestartet für %zu Iterationen...\n", iterations);

    // Hauptschleife: Führt die Messung für jede Iteration durch.
    for (size_t i = 0; i < iterations; ++i) {
        uint64_t t0, t1;
        uint64_t d_open = 0, d_write = 0, d_read = 0, d_close = 0;

        // --- 1. Messung: open (CreateFileA) ---
        t0 = now_us();
        HANDLE h = CreateFileA(path, GENERIC_READ | GENERIC_WRITE, 0, NULL,
                               OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
        t1 = now_us();

        if (h == INVALID_HANDLE_VALUE) {
            fprintf(stderr, "CreateFileA (open) ist in Iteration %zu fehlgeschlagen.\n", i);
            continue; // Diese Iteration überspringen, wenn open fehlschlägt
        }
        d_open = t1 - t0;

        // --- 2. Messung: write (WriteFile) ---
        t0 = now_us();
        DWORD written = 0;
        // Fehlerbehandlung: Prüfen, ob der Schreibvorgang erfolgreich war.
        if (!WriteFile(h, wbuf, wlen, &written, NULL) || written != wlen) {
            fprintf(stderr, "WriteFile ist in Iteration %zu fehlgeschlagen.\n", i);
        } else {
            t1 = now_us();
            d_write = t1 - t0;
        }

        // --- 3. Messung: read (ReadFile) ---
        // Dateizeiger auf den Anfang der Datei zurücksetzen für einen konsistenten Lesevorgang.
        LARGE_INTEGER offset;
        offset.QuadPart = 0;
        SetFilePointerEx(h, offset, NULL, FILE_BEGIN);

        char rbuf[16]; // Lesepuffer
        t0 = now_us();
        DWORD read_bytes = 0;
        // Fehlerbehandlung: Prüfen, ob der Lesevorgang erfolgreich war.
        if (!ReadFile(h, rbuf, wlen, &read_bytes, NULL) || read_bytes != wlen) {
            fprintf(stderr, "ReadFile ist in Iteration %zu fehlgeschlagen.\n", i);
        } else {
            t1 = now_us();
            d_read = t1 - t0;
        }

        // --- 4. Messung: close (CloseHandle) ---
        t0 = now_us();
        CloseHandle(h);
        t1 = now_us();
        d_close = t1 - t0; 

        // Gemessene Latenzen als eine Zeile in die CSV-Datei schreiben.
        fprintf(csv_file, "%llu,%llu,%llu,%llu\n",
                (unsigned long long)d_open,
                (unsigned long long)d_write,
                (unsigned long long)d_read,
                (unsigned long long)d_close);
    }

    // CSV-Datei schließen, um alle Puffer zu leeren und die Datei freizugeben.
    fclose(csv_file);

    // Aufräumen: Temporäre Datei löschen.
    DeleteFileA(path);

    // Bestätigung für den Benutzer ausgeben.
    printf("Messung erfolgreich abgeschlossen. %zu Messwerte wurden in '%s' geschrieben.\n",
           iterations, csv_path);

    return 0;
}