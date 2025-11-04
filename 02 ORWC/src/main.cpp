#include "components/benchmark.h"

int main(){
    ORWCBenchmark* bench = new ORWCBenchmark(1000);
    bench->run();
    bench->print_results();
    bench->export_csv("orwc_benchmark.csv");
    delete bench;
    return 0;
}