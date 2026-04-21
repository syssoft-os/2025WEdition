#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/spinlock.h>
#include <linux/ktime.h>
#include <linux/slab.h>
#include <linux/vmalloc.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Robert Mersiowsky");
MODULE_DESCRIPTION("spinlock latency measure");

#define ITERS 1000000

static spinlock_t lock;
static u64 *measurements;
static int num_measurements = 0;

static void measure_uncontended(void){
    
    int i;
    u64 start, end;

    num_measurements = 0;

    for(i = 0; i < ITERS; i++){
        start = ktime_get_ns();
        spin_lock(&lock);
        spin_unlock(&lock);
        end = ktime_get_ns();

        measurements[i] = end - start;
        num_measurements++;
    }
}

static int spinlock_proc_output(struct seq_file *m, void *v){
    int i;

    measure_uncontended();

    for(i = 0; i < num_measurements; i++){
        seq_printf(m,"%llu\n", measurements[i]);
    }

    return 0;
}

static int spinlock_proc_open(struct inode *inode, struct file *file){
    return single_open(file, spinlock_proc_output, NULL);
}

static const struct proc_ops spinlock_proc_ops = {
    .proc_open = spinlock_proc_open,
    .proc_read = seq_read,
    .proc_lseek = seq_lseek,
    .proc_release = single_release,
};

// module initialisation
static int __init spinlock_kernel_init(void){
    
    printk(KERN_INFO "Spinlock measurement module loaded\n");

    // allocate memory for measurements
    measurements = vmalloc(ITERS * sizeof(u64));
    if(!measurements){
        printk(KERN_ERR "Failed to allocate memory\n");
        return -ENOMEM;
    }

    // initialise spinlock
    spin_lock_init(&lock);

    // create /proc/spinlock_kernel file
    proc_create("spinlock_kernel", 0444, NULL, &spinlock_proc_ops);

    return 0;
}

static void __exit spinlock_kernel_exit(void){
    remove_proc_entry("spinlock_kernel", NULL);
    vfree(measurements);
    printk(KERN_INFO "Spinlock measurement module unloaded\n");
}

module_init(spinlock_kernel_init);
module_exit(spinlock_kernel_exit);
