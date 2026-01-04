#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <ctype.h>

void bug(const char *msg) {
    fprintf(stderr, "Crash: %s\n", msg);
    *((char *)(1)) = 1;
}

void vulnerable_function(const char *input) {
    // bug caused by long length
    // bug caused by short length
    // bug requires good corpus
    if (strlen(input) > 5) {
        fprintf(stderr, "len > 5\n");
        if (strlen(input) > 10) {
            fprintf(stderr, "len > 10\n");
            if (strlen(input) > 15) {
                fprintf(stderr, "len > 15\n");
                if (strlen(input) > 20) {
                    fprintf(stderr, "len > 20\n");
                    if (strlen(input) > 25) {
                        fprintf(stderr, "len > 25\n");
                        if (strlen(input) > 30) {
                            fprintf(stderr, "len > 30\n");
                            if (strlen(input) > 35) {
                                fprintf(stderr, "len > 35\n");
                                if (strlen(input) > 40) {
                                    fprintf(stderr, "len > 40\n");
                                    bug("long length");
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    if (input[0] == 's') {
        fprintf(stderr, "s\n");
        if (strlen(input) >= 1 && strlen(input) <= 3) {
            bug("short length");
        }
    }

    if (isupper(input[0])) {
        fprintf(stderr, "0 isupper\n");
        if (isupper(input[3])) {
            fprintf(stderr, "3 isupper\n");
            if (isupper(input[6])) {
                fprintf(stderr, "6 isupper\n");
                if (isupper(input[9])) {
                    fprintf(stderr, "9 isupper\n");
                    if (isupper(input[12])) {
                        fprintf(stderr, "12 isupper\n");
                        bug("isupper sequence");
                    }
                }
            }
        
        }
    }
    if (input[0] == 'a') {
        fprintf(stderr, "a\n");
        if (input[1] == 'b') {
            fprintf(stderr, "ab\n");
            if (input[2] == 'c') {
                fprintf(stderr, "abc\n");
                if (input[3] == 'd') {
                    fprintf(stderr, "abcd\n");
                    if (input[4] == 'e') {
                        fprintf(stderr, "abcde\n");
                        if (input[5] == 'f') {
                            fprintf(stderr, "abcdef\n");
                            bug("hard char sequence");
                        }
                    }
                }
            }
        }
    }
}

int main() {
    char buf[4096] = {0};
    read(0, buf, sizeof(buf));
    buf[sizeof(buf)-1] = '\0';
    vulnerable_function(buf);
    return 0;
}