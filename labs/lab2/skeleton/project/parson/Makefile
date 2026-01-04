CC=clang
CFLAGS=-I parson -g -Wall
SRC=harness.c parson/parson.c 
SANCOV_FLAGS=-fsanitize-coverage=trace-pc-guard

.PHONY: all instrument afl clean

all:
	$(CC) $(CFLAGS) $(SRC) -o harness

instrument:
	$(CC) -c $(CFLAGS) $(SANCOV_FLAGS) parson/parson.c -o parson_instrument.o
	llvm-ar rc libparson_instrument.a parson_instrument.o
	$(CC) $(CFLAGS) harness.c ../../sancov.c libparson_instrument.a -o harness

afl:
	../../aflpp/bin/afl-cc $(CFLAGS) $(SRC) -o afl_harness

clean:
	rm -f harness afl_harness parson_instrument.o libparson_instrument.a
