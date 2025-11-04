#include "orwc.h"

ORWC::ORWC() {
    open_time = 0;
    read_time = 0;
    write_time = 0;
    close_time = 0;
}

void ORWC::start() {
    string filepath = "tmp.txt";
    Stopwatch stopwatch;

    fstream file;

    // Measure open
    stopwatch.reset();
    stopwatch.start();
    file.open(filepath, ios::in | ios::out | ios::trunc);
    open_time = stopwatch.elapsed_milliseconds();

    // Measure write
    stopwatch.reset();
    stopwatch.start();
    file.write("A", 1);
    file.flush();
    write_time = stopwatch.elapsed_milliseconds();

    // Measure read (seek and read 1 byte)
    stopwatch.reset();
    stopwatch.start();
    file.seekg(0, ios::beg);
    char ch{};
    file.read(&ch, 1);
    read_time = stopwatch.elapsed_milliseconds();

    // Measure close
    stopwatch.reset();
    stopwatch.start();
    file.close();
    close_time = stopwatch.elapsed_milliseconds();

    // delete the file
    remove(filepath.c_str());
}