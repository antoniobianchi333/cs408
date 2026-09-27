#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

void vulnerable_function(const char *input) {
    char buffer[101];
    strncpy(buffer, input, 100);
    buffer[100] = '\0';
    input = buffer;

    if (strncmp(input, "head ", 5) != 0) {
        fprintf(stderr, "Input does not start with 'head '.\n");
        return;
    }

    input += 5;

    char *space_ptr = strchr(input, ' ');
    if (!space_ptr) {
        fprintf(stderr, "No space found after the string.\n");
        return;
    }

    int str_length = space_ptr - input;
    if (str_length > 8) {
        fprintf(stderr, "Crash: string length greater than 8.\n");
        *((char *)(1)) = 1;
    }

    char str[9];
    strncpy(str, input, str_length);
    str[str_length] = '\0';

    input = space_ptr + 1;

    char *end_ptr;
    long number = strtol(input, &end_ptr, 10);
    if (*end_ptr != '\0' || end_ptr == input) {
        fprintf(stderr, "Crash: No valid number found.\n");
        *((char *)(1)) = 1;
    }

    if (number > str_length) {
        fprintf(stderr, "Hung: number is greater than string length.\n");
        sleep(1000000);
    }

    for (int i = 0; i < number; i++) {
        putchar(str[i]);
    }
    puts("");
}