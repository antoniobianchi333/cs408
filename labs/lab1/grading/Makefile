# TA: Updated: 2025/12/15
# ---------------------------------- #
# DO NOT MODIFY THIS FILE            #
# ---------------------------------- #

# General
SRC = *.c
SRC_COVERAGE_TESTS = $(wildcard coverage_tests/*.c)
COVERAGE_TESTS_PRGS = $(patsubst %.c,%,$(SRC_COVERAGE_TESTS))
SRC_DETECTOR_TESTS = $(wildcard detector_tests/*.c)
DETECTOR_TESTS_PRGS = $(patsubst %.c,%,$(SRC_DETECTOR_TESTS))
CC = gcc

# Flags
STD    = -std=gnu11
WARN   = -Wall -Wextra -Wshadow -Wno-unused-parameter

FLAGS  = $(STD) $(WARN) -O2 -g3 -fPIC -I libunwind/include/ -ldl
CFLAGS = $(FLAGS) -march=native

COVERAGE_FLAGS =
ifneq ($(strip $(coverage)),)
COVERAGE_FLAGS += --coverage
endif

build_coverage_tests: COVERAGE_FLAGS += --coverage

# Targets
library:
	$(CC) $(CFLAGS) $(SRC) $(LIBS) -c $(COVERAGE_FLAGS)
	$(CC) -o testlib.so testlib.o utils.o libunwind/lib/libunwind*.a -shared $(COVERAGE_FLAGS) -ldl

# Coverage tests

#$(TEST_PRGS): %: %.c
$(COVERAGE_TESTS_PRGS): %: %.c
	$(CC) $(CFLAGS) -ldl -pthread -o $@ $<

build_coverage_tests: $(COVERAGE_TESTS_PRGS) library

run_coverage_tests: build_coverage_tests
	python3 coverage_tests_helper.py -n 10 -st 1 -seed 9

# Detector tests

$(DETECTOR_TESTS_PRGS): %: %.c
	$(CC) $(CFLAGS) -ldl -pthread -o $@ $<

build_detector_tests: $(DETECTOR_TESTS_PRGS) library

run_dectector_tests: build_detector_tests
	python3 detector_tests_helper.py -s random -n 100 -st false -seed 1 -detector crash,perf,dr,memory

# Other commands

clean:
	for prg in $(COVERAGE_TESTS_PRGS) ; do \
	  rm -f $$prg ; \
	done
	for prg in $(DETECTOR_TESTS_PRGS) ; do \
	  rm -f $$prg ; \
	done
	rm -f testlib.so
	rm -f ./*.o
	rm -f ./*.gcda
	rm -f ./*.gcov
	rm -f ./*.gcno

indent:
	clang-format -i *.[ch]
	clang-format -i */*.[ch]
	clang-format -i */*/*.[ch]
