# 03 Active Waiting – Spinlock-Latenz (macOS)
CC     = clang
CFLAGS = -std=c11 -O2
SRC    = aw.c

.PHONY: all clean

all: aw_atomic aw_unfair

# C11-atomic spinlock
aw_atomic: $(SRC)
	$(CC) $(CFLAGS) -o $@ $<

# Apples os_unfair_lock
aw_unfair: $(SRC)
	$(CC) $(CFLAGS) -DUSE_UNFAIR -o $@ $<

clean:
	rm -f aw_atomic aw_unfair