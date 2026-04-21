# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -O2 -pthread
LDFLAGS = -pthread -lm

# Directories
BUILD_DIR = build
KERNEL_BUILD_DIR = $(BUILD_DIR)/kernel
OUTPUT_DIR = output

# User-space source files and executables
SOURCES = filesystem.c semaphore.c pipe.c
TARGETS = filesystem semaphore pipe
EXECUTABLES = $(addprefix $(BUILD_DIR)/,$(TARGETS))

# Kernel module source
KERNEL_SOURCE = spinlock_kernel.c
KERNEL_MODULE = $(KERNEL_BUILD_DIR)/spinlock_kernel.ko
KDIR := /lib/modules/$(shell uname -r)/build

# Default target - build everything
all: userspace kernel

# Build user-space programs
userspace: $(BUILD_DIR) $(EXECUTABLES)

# Build kernel module
kernel: $(KERNEL_BUILD_DIR)
	# Copy source to build directory
	cp $(KERNEL_SOURCE) $(KERNEL_BUILD_DIR)/
	# Create Makefile in build directory
	echo "obj-m += spinlock_kernel.o" > $(KERNEL_BUILD_DIR)/Makefile
	# Build the module
	$(MAKE) -C $(KDIR) M=$(PWD)/$(KERNEL_BUILD_DIR) modules

# Create build directories
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(KERNEL_BUILD_DIR):
	mkdir -p $(KERNEL_BUILD_DIR)

$(OUTPUT_DIR):
	mkdir -p $(OUTPUT_DIR)

# Pattern rule for compiling user-space C files
$(BUILD_DIR)/%: %.c
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

# Kernel module targets
kernel-install:
	sudo insmod $(KERNEL_MODULE)

kernel-uninstall:
	sudo rmmod spinlock_kernel

kernel-csv: $(OUTPUT_DIR)
	cat /proc/spinlock_kernel > $(OUTPUT_DIR)/spinlock.csv
	@echo "CSV saved to: $(OUTPUT_DIR)/spinlock.csv"

# Clean targets
clean: clean-userspace clean-kernel

clean-userspace:
	rm -rf $(BUILD_DIR)

clean-kernel:
	rm -rf $(KERNEL_BUILD_DIR)

# Phony targets
.PHONY: all userspace kernel kernel-install kernel-uninstall kernel-csv clean clean-userspace clean-kernel help

# Help target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Build targets:"
	@echo "  all              - Build all user-space programs and kernel module (default)"
	@echo "  userspace        - Build only user-space programs"
	@echo "  kernel           - Build only kernel module"
	@echo ""
	@echo "Kernel module targets:"
	@echo "  kernel-install   - Load the kernel module (requires sudo)"
	@echo "  kernel-uninstall - Unload the kernel module (requires sudo)"
	@echo "  kernel-csv       - Extract data from /proc to output/spinlock.csv"
	@echo ""
	@echo "Clean targets:"
	@echo "  clean            - Remove all build artifacts"
	@echo "  clean-userspace  - Remove only user-space build artifacts"
	@echo "  clean-kernel     - Remove only kernel module build artifacts"
	@echo ""
	@echo "Output directories:"
	@echo "  build/           - User-space executables"
	@echo "  build/kernel/    - Kernel module build artifacts"
	@echo "  output/          - CSV output files"
	@echo ""
	@echo "Other:"
	@echo "  help             - Show this help message"