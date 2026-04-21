// measures active time spent in kernel - does not work for semaphores
// https://man.archlinux.org/man/perf_event_open.2.en
// https://elixir.bootlin.com/linux/v6.13.5/source/include/uapi/linux/perf_event.h#L389

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/perf_event.h>
#include <asm/unistd.h>
#include <pthread.h>
#include <semaphore.h>
#include <sched.h>
#include <math.h>

static void pin_to_cpu(int cpu){
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if(sched_setaffinity(0, sizeof(set), &set) != 0)
        perror("sched_setaffinity");
}

// wrapper for perf_event_open syscall - no glibc wrapper in linux for this syscall
static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid, 
                            int cpu, int group_fd, unsigned long flags){

    return syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
}

// setup perf counter for active cpu cycles - returns fd for perf counter
static int setup_perf_kernel_time(void){
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(struct perf_event_attr));
    
    pe.type = PERF_TYPE_SOFTWARE;               // software event
    pe.size = sizeof(struct perf_event_attr);
    pe.config = PERF_COUNT_SW_CPU_CLOCK;        // count CPU clock time
    pe.disabled = 1;            // start disabled
    pe.exclude_user = 1;        // exclude user-space time
    pe.exclude_kernel = 0;      // include kernel-space time
    pe.exclude_hv = 1;          // exclude hypervisor time

    int fd = perf_event_open(&pe, 0, -1, -1, 0);
    if(fd == -1){
        perror("perf_event_open");
        fprintf(stderr, "Note: run as root or try sudo sysctl -w kernel.perf_event_paranoid=-1\n");
        return -1;
    }

    return fd;
}


// read current perf counter value - returns counter value in ns or -1
static long long read_perf_counter(int fd){
    long long count;
    if(read(fd, &count, sizeof(long long)) != sizeof(long long)){
        perror("read perf counter");
        return -1;
    }
    return count;
}

// worker thread context
typedef struct{
    sem_t *req;
    sem_t *ack;
    double *measurements;
    int count;
    volatile int ready;
    int perf_fd;
} worker_ctx_t;


// worker thread function - measures CPU time spent in kernel processing (syscall overhead)
void *worker(void *arg){
    pin_to_cpu(1);
    worker_ctx_t *ctx = arg;

    ctx->ready = 1;

    for(int i=0; i < ctx->count; i++){

        // reset counter to 0 and enable it
        ioctl(ctx->perf_fd, PERF_EVENT_IOC_RESET, 0);
        ioctl(ctx->perf_fd, PERF_EVENT_IOC_ENABLE, 0);
        
        // read counter value
        long long start = read_perf_counter(ctx->perf_fd);

        // Blocking call
        sem_wait(ctx->req);

        // read counter value
        long long end = read_perf_counter(ctx->perf_fd);

        // Disable perf counter
        ioctl(ctx->perf_fd, PERF_EVENT_IOC_DISABLE, 0);

        ctx->measurements[i] = (double)(end - start);
        printf("start: %lld end: %lld measurements: %.2f\n", start, end, ctx->measurements[i]);

        // signal completion
        sem_post(ctx->ack);
    }
    return NULL;
}


int main(void){

    pin_to_cpu(0);

    const int iters = 10000;
    double *measurements = malloc(iters * sizeof(double));

    // setup perf counter for kernel time
    int perf_fd = setup_perf_kernel_time();
    if(perf_fd < 0){
        perror("Failed to setup perf counter");
        free(measurements);
        return 1;
    }

    sem_t req, ack;
    sem_init(&req, 0, 0);
    sem_init(&ack, 0, 0);

    worker_ctx_t ctx = {&req, &ack, measurements, iters, 0, perf_fd};

    pthread_t thread;
    if (pthread_create(&thread, NULL, worker, &ctx)){
        perror("pthread_create");
        close(perf_fd);
        free(measurements);
        sem_destroy(&req);
        sem_destroy(&ack);
        return 1;
    }


    while(!ctx.ready){
        usleep(1);
    }
    usleep(10000);

    // release worker repeatedly
    for(int i = 0; i < iters; i++){
        usleep(50);
        sem_post(&req);
        sem_wait(&ack);
    }

    pthread_join(thread, NULL);

    FILE* csv_krnl = fopen("semaphore_kernel.csv", "w");
    if(csv_krnl == NULL){
        perror("csv_krnl fopen");
        close(perf_fd);
        free(measurements);
        sem_destroy(&req);
        sem_destroy(&ack);
        return 1;
    }

    for (int j = 0; j < iters; j++){
        if (j != 0){
            fprintf(csv_krnl, ",");
        }
        fprintf(csv_krnl, "%.18f", measurements[j]);
    }

    fclose(csv_krnl);
    close(perf_fd);
    free(measurements);
    sem_destroy(&req);
    sem_destroy(&ack);
    return 0;
}