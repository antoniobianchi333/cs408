#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main() {
        char buf[4096] = {0};
        read(0, buf, sizeof(buf));
        buf[sizeof(buf)-1] = '\0';

        if (strlen(buf) == 7) {
                fprintf(stderr, "Crash: string length is equal to 7.\n");
                *((char *)(1)) = 1;
        } else if (strlen(buf) == 9) {
                fprintf(stderr, "Hung: string length is equal to 11.\n");
                sleep(100000);
        }
        return 0;
}