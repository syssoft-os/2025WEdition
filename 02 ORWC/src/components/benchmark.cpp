#include "benchmark.h"

ORWCBenchmark::ORWCBenchmark(int num_runs){
    this->num_runs = num_runs;
}

ORWCBenchmark::~ORWCBenchmark() {
    delete[] orwc_ptr;
}

void ORWCBenchmark::export_csv(const string& filename) const {
    ofstream file(filename);
    file << "Open,Read,Write,Close\n";
    for (int i = 0; i < this->num_runs; ++i) {
        file << orwc_ptr[i].get_open_time_ms() << "," << orwc_ptr[i].get_read_time_ms() << "," << orwc_ptr[i].get_write_time_ms() << "," << orwc_ptr[i].get_close_time_ms() << "\n";
    }
    file.close();
}

void ORWCBenchmark::run() {
    // allocate memory for the ORWC objects
    this->orwc_ptr = new ORWC[this->num_runs];

    // run the benchmark for each ORWC object
    for (int i = 0; i < this->num_runs; ++i) {
        orwc_ptr[i].start();
    }

    // calculate the average time
    double sum_open = 0.0;
    double sum_read = 0.0;
    double sum_write = 0.0;
    double sum_close = 0.0;

    for (int i = 0; i < this->num_runs; ++i) {
        sum_open  += orwc_ptr[i].get_open_time_ms();
        sum_read  += orwc_ptr[i].get_read_time_ms();
        sum_write += orwc_ptr[i].get_write_time_ms();
        sum_close += orwc_ptr[i].get_close_time_ms();
    }

    avg_open  = sum_open  / this->num_runs;
    avg_read  = sum_read  / this->num_runs;
    avg_write = sum_write / this->num_runs;
    avg_close = sum_close / this->num_runs;
}

void ORWCBenchmark::print_results() const {
    std::cout << "Average Open:  " << avg_open  << " ms\n";
    std::cout << "Average Read:  " << avg_read  << " ms\n";
    std::cout << "Average Write: " << avg_write << " ms\n";
    std::cout << "Average Close: " << avg_close << " ms\n";
}