#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <pthread.h>
#include <semaphore.h>
#include <sched.h>
#include <unistd.h>
#include <math.h>

static void pin_to_cpu(int cpu){
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if(sched_setaffinity(0, sizeof(set), &set) != 0)
        perror("sched_setaffinity");
}

static inline double timespec_diff(struct timespec start, struct timespec end){
    return (end.tv_sec - start.tv_sec) * 1e9 + (end.tv_nsec - start.tv_nsec);
}

typedef struct {
    sem_t *req;
    sem_t *ack;
    double *measurements;
    int count;
    int ready;
} worker_ctx_t;

// worker function
void *worker(void *arg){
    pin_to_cpu(1);

    worker_ctx_t *ctx = arg;
    struct timespec start, end;

    ctx->ready = 1;

    // Warmup
    for(int i = 0; i < 100; i++){
        sem_wait(ctx->req);
        sem_post(ctx->ack);
    }

    for(int i = 0; i < ctx->count; i++){

        // measurement
        clock_gettime(CLOCK_MONOTONIC, &start);
        sem_wait(ctx->req);
        sem_post(ctx->ack);
        clock_gettime(CLOCK_MONOTONIC, &end);
        ctx->measurements[i] = timespec_diff(start, end);
    }
    return NULL;
}

int main(void){

    pin_to_cpu(0);

    const int iters = 1000000;
    double *measurements = malloc(iters * sizeof(double));

    sem_t req, ack;
    sem_init(&req, 0, 0);
    sem_init(&ack, 0, 0);

    worker_ctx_t ctx = {&req, &ack, measurements, iters, 0};

    pthread_t thread;
    if(pthread_create(&thread, NULL, worker, &ctx)){
        perror("pthread_create");
        free(measurements);
        sem_destroy(&req);
        sem_destroy(&ack);
        return 1;
    }

    // wait for worker to be blocked a sem_wait()
    while(!ctx.ready){
        usleep(1);
    }

    usleep(10000);

    // Warmup
    for(int i = 0; i < 100; i++){
        usleep(50);
        sem_post(&req);
        sem_wait(&ack);
    }

    for(int i = 0; i < iters; i++){
        usleep(50);
        sem_post(&req);
        sem_wait(&ack);
    }

    pthread_join(thread, NULL);

    FILE* csv_sem = fopen("../output/semaphore.csv", "w");
    if(csv_sem == NULL){
        perror("csv_sem fopen");
        free(measurements);
        sem_destroy(&req);
        sem_destroy(&ack);
        return 1;
    }

    for (int j = 0; j < iters; j++){
        fprintf(csv_sem, "%.2f\n", measurements[j]);
    }

    fclose(csv_sem);
    free(measurements);
    sem_destroy(&req);
    sem_destroy(&ack);
    return 0;
}