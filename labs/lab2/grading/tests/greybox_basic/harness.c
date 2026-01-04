#include <stdio.h>
#include <string.h>

int main() {
        char buf[4096] = {0};
        read(0, buf, sizeof(buf));
        buf[sizeof(buf)-1] = '\0';
        if (strlen(buf) >= 1 && strlen(buf) <= 4 ) {
                fprintf(stderr, "4 >= buf len >= 1\n");
        }
        if (strlen(buf) >= 5 && strlen(buf) <= 10) {
                fprintf(stderr, "7 >= buf len >= 3\n");
                *((char *)(1)) = 1;
        }
        return 0;
}