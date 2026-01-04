#include <stdio.h>
#include <string.h>

int main() {
        char buf[4096] = {0};
        read(0, buf, sizeof(buf));
        buf[sizeof(buf)-1] = '\0';
        // get current working directory using getcwd
        char dir[4096];
        getcwd(dir, sizeof(dir));
        // append the buf to the file dir/input.txt
        FILE *f = fopen(strcat(dir, "/input.txt"), "a");
        fprintf(f, "%s\n", buf);
        return 0;
}