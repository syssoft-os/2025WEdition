#include <iostream>
#include <fstream>
#include <unistd.h>
#include <cerrno>
#include <cstring>
#include <cstdlib>
#include "stopwatch.h"
#include <sys/wait.h>

// Pipe latency measurement between two processes using fork().


int main(int argc, char *argv[]) {

    // Number of iterations
    int iterations = 1000000;
    const char *out_filename = "ipc_pipe.csv";

    std::cout << "Interprocess Pipe latency benchmark" << std::endl;
    std::cout << "Iterations: " << iterations << ", output: " << out_filename << std::endl;

    std::ofstream csv(out_filename);
    if (!csv.is_open()) {
        std::cerr << "Failed to open output file: " << out_filename << std::endl;
        return 1;
    }

    // CSV header
    csv << "iteration,latency_us_interprocess)" << std::endl;

    // Zwei Pipes für bidirektionale Kommunikation
    int pipe_A[2]; // A -> B
    int pipe_B[2]; // B -> A

    if (pipe(pipe_A) == -1) {
        perror("pipe_A");
        exit(EXIT_FAILURE);
    }
    if (pipe(pipe_B) == -1) {
        perror("pipe_B");
        exit(EXIT_FAILURE);
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        exit(EXIT_FAILURE);
    }

    Stopwatch sw;

    if (pid > 0) {
            // Elternprozess: Sender/Messer (A)
            // Schließt nicht benötigte Enden
            close(pipe_A[0]); // A liest nicht von A->B
            close(pipe_B[1]); // A schreibt nicht in B->A

            char ping = 'x';
            char pong;
            
            for (int i = 0; i < iterations; ++i) {
                sw.reset();
                sw.start();

                // Sende Ping an Kind
                if (write(pipe_A[1], &ping, 1) != 1) {
                    std::cerr << "A: write failed at iteration " << i << std::endl;
                    break;
                }

                // Warte auf Antwort (Pong)
                if (read(pipe_B[0], &pong, 1) != 1) {
                    std::cerr << "A: read failed at iteration " << i << std::endl;
                    break;
                }

                sw.stop();
                double us = sw.elapsed_microseconds();
                csv << i << "," << us << '\n';
            }

        close(pipe_A[1]);
        close(pipe_B[0]);
        csv.close();
        std::cout << "Done. Results written to " << out_filename << std::endl;
        // Warten auf Kindprozess
        wait(nullptr);
        return 0;
    } else {
        // Kindprozess: Empfänger/Antworter (B)
        // Schließt nicht benötigte Enden
        close(pipe_A[1]); // B schreibt nicht in A->B
        close(pipe_B[0]); // B liest nicht von B->A

        char ping;
        char pong = 'y';
        for (int i = 0; i < iterations; ++i) {
            // Warte auf Ping von Eltern
            if (read(pipe_A[0], &ping, 1) != 1) {
                std::cerr << "B: read failed at iteration " << i << std::endl;
                break;
            }
            // Sende Pong zurück
            if (write(pipe_B[1], &pong, 1) != 1) {
                std::cerr << "B: write failed at iteration " << i << std::endl;
                break;
            }
        }

        close(pipe_A[0]);
        close(pipe_B[1]);
        return 0;
    }
}
