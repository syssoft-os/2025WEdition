#include <iostream>
#include <fstream>
#include <fcntl.h>
#include <unistd.h>
#include <cstring>
#include <cstdlib>
#include <cassert>

#include "stopwatch.h"

using namespace std;

int main() {
    const int N = 100;
    const int BUFFER_SIZE = 1024;
    
    ofstream csv("results_stopwatch_nocache.csv");
    csv << "open,write,read,close\n";
    
    char buf[BUFFER_SIZE];
    memset(buf, 'A', BUFFER_SIZE);
    
    cout << "ORWC No-Cache Messung\n";
    cout << "Messungen: " << N << "\n\n";
    
    Stopwatch sw;
    
    unlink("test.dat");

    for (int i = 0; i < N; i++) {

        system("sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'"); //PageCache, Dentries und Inodes weg
        sync();
        

        sw.reset();
        sw.start();
        int fd = open("test.dat", O_RDWR | O_CREAT | O_TRUNC, 0644);
        sw.stop();

        double open_us = sw.elapsed_microseconds();
        assert(fd >= 0);



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
        
        csv << open_us << "," << write_us << ","
            << read_us << "," << close_us << "\n";
        
        if ((i+1) % 10 == 0) cout << (i+1) << "/" << N << "\n"; //anzeige fortschritt
    }
    
    unlink("test.dat");
    csv.close();
    cout << "\nGespeichert unter results_stopwatch_nocache.csv...\n";
    return 0;
}
