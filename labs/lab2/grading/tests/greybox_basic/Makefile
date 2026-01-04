CC=clang

.PHONY: all clean

all:
	$(CC) -O0 -c -g -fsanitize-coverage=trace-pc-guard harness.c -o harness.o
	$(CC) -c sancov.c -o sancov.o
	$(CC) harness.o sancov.o -o harness

clean:
	rm -f harness
