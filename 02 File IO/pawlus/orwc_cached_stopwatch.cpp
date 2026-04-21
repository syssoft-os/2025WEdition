#include <iostream>
#include <fstream>
#include <fcntl.h>
#include <unistd.h>
#include <cstring>
#include <cassert>

#include "stopwatch.h"

using namespace std;

int main() {
    const int N = 10000;
    const int WARMUP = 100;
    const int BUFFER_SIZE = 1024;

    ofstream csv("results_stopwatch.csv");
    
    csv << "open,write,read,close\n"; // Header der csv
    
    char buf[BUFFER_SIZE];
    memset(buf, 'A', BUFFER_SIZE);
    
    cout << "Warmup: " << WARMUP << " | Messungen: " << N << "\n\n";
    

    Stopwatch sw;
    unlink("test.dat"); // lösch, falls existiert

    for (int i = 0; i < N + WARMUP; i++) {
        bool record = (i >= WARMUP); //Flag für WarmUp true oder false

        sw.reset();
        sw.start();
        int fd = open("test.dat", O_RDWR | O_CREAT | O_TRUNC, 0644);
        sw.stop();

        double open_us = sw.elapsed_microseconds();
        assert(fd >= 0); // fd -1 == Fehler


        sw.reset();
        sw.start();
        ssize_t written = write(fd, buf, BUFFER_SIZE);
        sw.stop();

        double write_us = sw.elapsed_microseconds();
        assert(written == BUFFER_SIZE);
        

        lseek(fd, 0, SEEK_SET);
        

        sw.reset();
        sw.start();
        ssize_t read_bytes = read(fd, buf, BUFFER_SIZE);
        sw.stop();

        double read_us = sw.elapsed_microseconds();
        assert(read_bytes == BUFFER_SIZE);
        

        sw.reset();
        sw.start();
        int close_ret = close(fd);
        sw.stop();

        double close_us = sw.elapsed_microseconds();
        assert(close_ret == 0);
        

        if (record) {
            // in csv wenn record = True
            csv << open_us << "," << write_us << "," 
                << read_us << "," << close_us << "\n";
            
            // anzeige fortschritt
            int current_n = i - WARMUP + 1;
            if (current_n % 2000 == 0) cout << current_n << "/" << N << "\n";
        }
    }
    
    unlink("test.dat");
    csv.close();
    
    cout << "\nGespeichert in results_stopwatch.csv!\n";
    return 0;
}
