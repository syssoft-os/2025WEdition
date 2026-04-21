
CXX = g++

# Compiler flags
CXXFLAGS = -std=c++17 -O3 -I../Helper/include

# Linker flags: helper library is built in ../Helper
LDFLAGS = -L../Helper/lib -lhelper

# Output directory for binaries
BIN_DIR = bin

# Target executables
TARGETS = $(BIN_DIR)/pipe $(BIN_DIR)/ipc_pipe

all: helper $(TARGETS)

# Build helper library only once
helper:
	@cd ../Helper && $(MAKE)

# Build binaries in bin/

$(BIN_DIR)/pipe: src/pipe.cpp | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) -o $@ src/pipe.cpp $(LDFLAGS)

$(BIN_DIR)/ipc_pipe: src/ipc_pipe.cpp | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) -o $@ src/ipc_pipe.cpp $(LDFLAGS)

# Create bin directory if missing
$(BIN_DIR):
	mkdir -p $(BIN_DIR)

clean:
	rm -f $(BIN_DIR)/pipe $(BIN_DIR)/ipc_pipe
	@cd ../Helper && $(MAKE) clean || true

pipe: $(BIN_DIR)/pipe
	./$(BIN_DIR)/pipe

ipc_pipe: $(BIN_DIR)/ipc_pipe
	./$(BIN_DIR)/ipc_pipe

.PHONY: all clean pipe ipc_pipe helper
