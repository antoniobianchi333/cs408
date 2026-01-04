# General
SRC = *.c
SRC_TESTS = $(wildcard *.c)
TEST_PRGS = $(patsubst %.c,%,$(SRC_TESTS))
CC = gcc

# Flags
STD    = -std=gnu11
WARN   = -Wall -Wextra -Wshadow -Wno-unused-parameter

FLAGS  = $(STD) $(WARN) -O0 -g3

# Targets
$(TEST_PRGS): %: %.c
	$(CC) $(FLAGS) -ldl -pthread -o $@ $<

all: $(TEST_PRGS)

clean:
	for prg in $(TEST_PRGS) ; do \
	  rm -f $$prg ; \
	done
	rm -f ./*.o
