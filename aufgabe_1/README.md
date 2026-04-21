### directories

``` 
├── Source Files
│   ├── filesystem.c            # ORWC latency
│   ├── pipe.c                  # Pipe latency
│   ├── semaphore.c             # Semaphore latency
│   ├── spinlock_kernel.c       # Spinlock latency
│   └── data_analysis.py        # Plots and statistics
│
├── build/                      # Build artifacts
├── output/                     # CSV measurement data
├── analysis/                   # Generated plots
└── holzweg/                    # Experimental/dead-end code
```


### Spinlock measurements with kernel module

 1. Build the kernel module
```
    make kernel
```
 2. Load the module (requires sudo)
```
    make kernel-install
```
 or manually:
```
    sudo insmod build/kernel/spinlock_kernel.ko
```
 3. Verify it's loaded
```
    lsmod | grep spinlock
```
 or check kernel log:
```
    dmesg | tail
```
 4. Run the benchmark and save to CSV
```
    make kernel-csv
```
 or manually:
```    
    cat /proc/spinlock_kernel > output/spinlock.csv
```
 5. Unload the module when done
```    
    make kernel-uninstall
``` 
 or manually:
``` 
    sudo rmmod spinlock_kernel
```
 6. Verify it's unloaded
``` 
    lsmod | grep spinlock
``` 
 or check kernel log:
``` 
    dmesg | tail
```


### Graphs and statistics

Graphs and statistics can be created executing data_analysis.py from the command line:

    python data_analysis.py <csv_file> [output_name]

.csv files are stored in the output/ directory.

