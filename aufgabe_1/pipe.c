#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sched.h>
#include <string.h>
#include <math.h>
#include <fcntl.h>

static inline double timespec_diff(struct timespec start, struct timespec end){
    return (end.tv_sec-start.tv_sec) * 1e9 + (end.tv_nsec-start.tv_nsec);
}

static void pin_to_cpu (int cpu){
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if(sched_setaffinity(0, sizeof(set), &set) != 0)
        perror("sched_setaffinity");
}

int main(void){
    int pipefd[2];
    const int iters = 1000000;
    const int message_length = 64;
    char buffer[message_length];

    memset(buffer, 'A', message_length);

    pin_to_cpu(0);

    // create pipe
    if(pipe(pipefd) == -1){
        perror("create pipe");
        return 1;
    }

    // set pipe to nonblocking
    fcntl(pipefd[0], F_SETFL, O_NONBLOCK);
    fcntl(pipefd[1], F_SETFL, O_NONBLOCK);

    double *write_measurements = malloc(iters * sizeof(double));
    double *read_measurements = malloc(iters * sizeof(double));

    struct timespec start, end;

    // write

    //warmup
    write(pipefd[1], buffer, message_length);

    for(int i = 0; i < iters; i++){
        clock_gettime(CLOCK_MONOTONIC, &start);
        ssize_t n = write(pipefd[1], buffer, message_length);
        clock_gettime(CLOCK_MONOTONIC, &end);

        if (n < 0) {
            // drain pipe
            char drain[65536];
            read(pipefd[0], drain, sizeof(drain));
            i--;
            continue;
        }
        write_measurements[i] = timespec_diff(start, end);
    }

    // read

    for(int i = 0; i < iters; i++){
        write(pipefd[1], buffer, message_length);
    }

    // warmup
    read(pipefd[0], buffer, message_length);

    for (int i = 0; i < iters; i++){
        
        write(pipefd[1], buffer, message_length);
        clock_gettime(CLOCK_MONOTONIC, &start);
        ssize_t n = read(pipefd[0], buffer, message_length);
        clock_gettime(CLOCK_MONOTONIC, &end);


        if(n != message_length){
            fprintf(stderr, "read error at iteration %d\n", i);
            break;
        }

         read_measurements[i] = timespec_diff(start, end);
    }

    close(pipefd[0]);
    close(pipefd[1]);

    // write output
    FILE* csv_write = fopen("../output/pipe_write.csv", "w");
    if(csv_write == NULL){
        perror("fopen csv_write");
        free(write_measurements);
        free(read_measurements);
        return 1;
    }

    for(int i = 0; i < iters; i++){
        fprintf(csv_write, "%.2f\n", write_measurements[i]);
    }

    free(write_measurements);
    fclose(csv_write);

    // read output
    FILE* csv_read = fopen("../output/pipe_read.csv", "w");
    if(csv_read == NULL){
        perror("fopen csv_read");
        free(read_measurements);
        return 1;
    }

    for(int i = 0; i < iters; i++){
        fprintf(csv_read, "%.2f\n", read_measurements[i]);
    }

    free(read_measurements);
    fclose(csv_read);

}