CXX := g++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra -I../Helper/include -Isrc
LDFLAGS := -L../Helper/lib
LDLIBS := -lhelper

BUILD_DIR := build
TARGET := $(BUILD_DIR)/orwc
SOURCES := src/main.cpp src/components/orwc.cpp src/components/benchmark.cpp
OBJECTS := $(patsubst src/%.cpp,$(BUILD_DIR)/%.o,$(SOURCES))
HELPER_LIB := ../Helper/lib/libhelper.a

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJECTS) $(HELPER_LIB) | $(BUILD_DIR)
	$(CXX) $(OBJECTS) -o $@ $(LDFLAGS) $(LDLIBS)

$(HELPER_LIB):
	$(MAKE) -C ../Helper

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/%.o: src/%.cpp | $(BUILD_DIR)
	mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -rf $(BUILD_DIR)

