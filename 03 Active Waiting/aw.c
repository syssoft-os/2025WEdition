#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <mach/mach_time.h>
#include <math.h>

#ifdef USE_UNFAIR
#include <os/lock.h>
static os_unfair_lock lock = OS_UNFAIR_LOCK_INIT;
static inline void my_lock(void) { os_unfair_lock_lock(&lock); }
static inline void my_unlock(void) { os_unfair_lock_unlock(&lock); }
#else
#include <stdatomic.h>
static atomic_flag lock = ATOMIC_FLAG_INIT;
static inline void my_lock(void)
{
  while (atomic_flag_test_and_set_explicit(&lock, memory_order_acquire))
  { /* busy‐wait */
  }
}
static inline void my_unlock(void)
{
  atomic_flag_clear_explicit(&lock, memory_order_release);
}
#endif

static mach_timebase_info_data_t tb = {0, 0};
static inline uint64_t now_ns(void)
{
  uint64_t t = mach_absolute_time();
  return (t * tb.numer) / tb.denom;
}

int main(int argc, char **argv)
{
  bool csv = false;
  char *csv_file = NULL;
  int idx = 1;

  if (argc > 2 && strcmp(argv[1], "--csv") == 0)
  {
    csv = true;
    csv_file = argv[2];
    idx = 3;
  }

  uint64_t n = 10000000ULL;
  if (idx < argc)
  {
    n = (uint64_t)atoll(argv[idx]);
    if (n == 0)
    {
      fprintf(stderr, "Ungültige Iterationszahl '%s'\n", argv[idx]);
      return 1;
    }
  }

  mach_timebase_info(&tb);

  double mean = 0.0, M2 = 0.0;
  uint64_t minimum = UINT64_MAX, maximum = 0;

  for (uint64_t i = 1; i <= n; i++)
  {
    uint64_t t0 = now_ns();
    my_lock();
    my_unlock();
    uint64_t dt = now_ns() - t0;

    /* Welford‐Online‐Varianz */
    double delta = (double)dt - mean;
    mean += delta / i;
    M2 += delta * ((double)dt - mean);

    if (dt < minimum)
      minimum = dt;
    if (dt > maximum)
      maximum = dt;
  }

  double variance = M2 / (n - 1);
  double stddev = sqrt(variance);
  double ci95 = 1.96 * stddev / sqrt((double)n);

  const char *variant =
#ifdef USE_UNFAIR
      "os_unfair_lock";
#else
      "atomic_flag";
#endif

  printf("Lock-Variante: %s\n", variant);
  printf("Samples       = %llu\n", (unsigned long long)n);
  printf("Mean          = %.1f ns\n", mean);
  printf("Min           = %llu ns\n", (unsigned long long)minimum);
  printf("Max           = %llu ns\n", (unsigned long long)maximum);
  printf("Stddev        = %.1f ns\n", stddev);
  printf("95%% CI       = ±%.1f ns\n", ci95);

  if (csv)
  {
    bool newfile = false;
    FILE *ft = fopen(csv_file, "r");
    if (!ft)
    {
      newfile = true;
    }
    else
    {
      fclose(ft);
    }

    FILE *f = fopen(csv_file, "a");
    if (!f)
    {
      perror("fopen(append)");
    }
    else
    {
      if (newfile)
      {
        fprintf(f,
                "variant,samples,mean_ns,min_ns,max_ns,stddev_ns,ci95_ns\n");
      }
      fprintf(f,
              "%s,%llu,%.1f,%llu,%llu,%.1f,%.1f\n",
              variant,
              (unsigned long long)n,
              mean,
              (unsigned long long)minimum,
              (unsigned long long)maximum,
              stddev,
              ci95);
      fclose(f);
      printf("DEBUG: CSV appended to '%s'\n", csv_file);
    }
  }

  return 0;
}