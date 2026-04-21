#include <iostream>
#include <fstream>
#include <unistd.h>
#include <cerrno>
#include <cstring>
#include <cstdlib>
#include "stopwatch.h"

int main(int argc, char *argv[]) {

    // Number of iterations
    int iterations = 1000000;
    const char *out_filename = "pipe.csv";

    std::cout << "Pipe latency benchmark" << std::endl;
    std::cout << "Iterations: " << iterations << ", output: " << out_filename << std::endl;

    std::ofstream csv(out_filename);
    if (!csv.is_open()) {
        std::cerr << "Failed to open output file: " << out_filename << std::endl;
        return 1;
    }

    // CSV header
    csv << "iteration,latency_us" << std::endl;

    Stopwatch sw;

    // Measurement loop: measure each pipe() call separately
    for (int i = 0; i < iterations; ++i) {
        
        int fds[2];

        if (pipe(fds) != 0) {
            std::cerr << "pipe() failed at iteration " << i << ": " << std::strerror(errno) << std::endl;
            continue;
        }

        sw.reset();
        sw.start();

        write(fds[1], "x", 1); // Write a byte to the pipe
        char buf;
        read(fds[0], &buf, 1);  // Read the byte back

        // Stop measurement
        sw.stop();
        double us = sw.elapsed_microseconds();

        // Close fds quickly to avoid leaking
        close(fds[0]);
        close(fds[1]);

        // Write to CSV. Use flush rarely; rely on ofstream buffer for speed.
        csv << i << "," << us << '\n';

        // Optionally print progress every so often
        // if ((i + 1) % 1000000 == 0) {
        //     std::cout << "Completed " << (i + 1) << " iterations" << std::endl;
        // }
    }


    csv.close();
    std::cout << "Done. Results written to " << out_filename << std::endl;
    return 0;
}
