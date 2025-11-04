#pragma once
#include "orwc.h"
#include <iostream>
using namespace std;

class ORWCBenchmark {
    public:
        ORWCBenchmark(int num_runs);
        ~ORWCBenchmark();
        void run();

        double average_open_ms() const { return avg_open; }
        double average_read_ms() const { return avg_read; }
        double average_write_ms() const { return avg_write; }
        double average_close_ms() const { return avg_close; }
        void print_results() const;
        void export_csv(const string& filename) const;

    private:
        int num_runs;
        ORWC* orwc_ptr;
        double avg_open = 0.0;
        double avg_read = 0.0;
        double avg_write = 0.0;
        double avg_close = 0.0;
};