# OS-Level Experiments (Winter 2025)

## 01 Context Switch

This folder contains experiments to measure the cost of context switches and system calls at the OS level.

### Content

- **cs.c**: A C program that measures the average time of system calls by repeatedly calling `syscall(SYS_getpid)` and calculating the overhead per call in microseconds.

- **Python Wrapper**: A Python-based wrapper that allows importing and calling C/C++ functions:
  - `cs.py`: Main Python script that uses the `Importer` utility to execute context switch measurements from both C and C++ implementations
  - `cs.c` & `cs.cpp`: C and C++ implementations with a `measure_context_switch()` function
  - `lib/Importer.py`: Utility for dynamically importing and executing C/C++ code from Python
  - `requirements.txt`: Python dependencies for the wrapper

- **Makefile**: Build configuration for compiling the C program

- **todo.md**: Future improvements and ideas including:
  - CSV output for multiple context switch measurements
  - Python scripts for data visualization
  - Higher resolution clock investigation
  - Refactoring into stopwatch class
  - Procedure call overhead measurements

### Usage

Compile and run the C program:
```bash
cd "01 Context Switch"
make
./cs
```

Or use the Python wrapper (requires gcc/g++):
```bash
cd "01 Context Switch/Python Wrapper"
pip install -r requirements.txt
python cs.py
```

