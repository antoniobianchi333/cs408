CC=clang

.PHONY: all clean

all:
	$(CC) -O0 -c -g -fsanitize-coverage=trace-pc-guard vulnerable.c -o vulnerable.o
	$(CC) -c sancov.c -o sancov.o
	$(CC) vulnerable.o sancov.o -o harness

clean:
	rm -f harness
