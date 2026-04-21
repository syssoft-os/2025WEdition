#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>
#include <sched.h>

static inline double timespec_diff(struct timespec start, struct timespec end){
    return (end.tv_sec - start.tv_sec) * 1e9 + (end.tv_nsec - start.tv_nsec);
}

static void pin_to_cpu(int cpu){
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if(sched_setaffinity(0, sizeof(set), &set) != 0){
        perror("sched-setaffinity");
    }
}

int main(void){

    pin_to_cpu(0);
    const size_t block_size = 4096;
    const int iters = 1000000;
    void *buf;
    int ret;
    struct timespec start, end;

    ret = posix_memalign(&buf, block_size, block_size);
    if(ret != 0){
        fprintf(stderr, "posix_memalign: %s\n", strerror(ret));
        return 1;
    }

    memset(buf, 0xAB, block_size);

    // open
    
    // open csv_open
    FILE *csv_open = fopen("../output/filesystem_open.csv", "w");
    if(csv_open == NULL){
        perror("fopen csv_open");
        free(buf);
        return 1;
    }

    // open csv_close
    FILE *csv_close = fopen("../output/filesystem_close.csv", "w");
    if(csv_close == NULL){
        perror("fopen csv_close");
        free(buf);
        return 1;
    }

    //warmup
    for(int i = 0; i < 100; i++){
        int fd_null = open("/dev/null", O_RDWR);
        if(fd_null < 0){
            perror("open /dev/null");
            free(buf);
            return 1;
        }
        close(fd_null);
    }


    for(int i = 0; i < iters; i++){

        clock_gettime(CLOCK_MONOTONIC, &start);
        int fd_null = open("/dev/null", O_RDWR);
        if(fd_null < 0){
            perror("open /dev/null");
            free(buf);
            return 1;
        }
        clock_gettime(CLOCK_MONOTONIC, &end);
        double latency = timespec_diff(start, end);
        fprintf(csv_open, "%.2f\n", latency);

        clock_gettime(CLOCK_MONOTONIC, &start);
        close(fd_null);
        clock_gettime(CLOCK_MONOTONIC, &end);
        latency = timespec_diff(start, end);
        fprintf(csv_close, "%.2f\n", latency);
    }
    fclose(csv_open);
    fclose(csv_close);

    // write

    int fd_null = open("/dev/null", O_RDWR);
    if(fd_null < 0){
        perror("open /dev/null");
        free(buf);
        return 1;
    }

    // open csv
    FILE *csv_write = fopen("../output/filesystem_write.csv", "w");
    if(csv_write == NULL){
        perror("fopen csv_write");
        close(fd_null);
        free(buf);
        return 1;
    }

    // warmup
    for (int i = 0; i < 100; i++)
        write(fd_null, buf, block_size);

    for(int i = 0; i < iters; i++){

        // measuring writes
        clock_gettime(CLOCK_MONOTONIC, &start);
        write(fd_null, buf, block_size);
        clock_gettime(CLOCK_MONOTONIC, &end);
        double latency = timespec_diff(start, end);
        fprintf(csv_write, "%.2f\n", latency);
    }
    fclose(csv_write);

    FILE* csv_read = fopen("../output/filesystem_read.csv", "w");
    if(csv_read == NULL){
        perror("fopen csv_read");
        close(fd_null);
        free(buf);
        return 1;
    }

    // warmup
    for(int i = 0; i < 100; i++)
        read(fd_null, buf, block_size);

    for (int i = 0; i < iters; i++){

        // measure reads    
        clock_gettime(CLOCK_MONOTONIC, &start);
        read(fd_null, buf, block_size);
        clock_gettime(CLOCK_MONOTONIC, &end);
        double latency = timespec_diff(start, end);
        fprintf(csv_read, "%.2f\n", latency);

    }
    fclose(csv_read);
    close(fd_null);
    free(buf);

    return 0;
}