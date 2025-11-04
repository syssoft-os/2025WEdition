#pragma once
#include <iostream>
#include <fstream>
#include "../../../Helper/include/stopwatch.h"
using namespace std;

class ORWC {
    public:
        // constructor
        ORWC();
        // run the benchmark
        void start();
        // getter
        double get_open_time_ms() const { return open_time; }
        double get_read_time_ms() const { return read_time; }
        double get_write_time_ms() const { return write_time; }
        double get_close_time_ms() const { return close_time; }
    private:
        double open_time;
        double read_time;
        double write_time;
        double close_time;
};