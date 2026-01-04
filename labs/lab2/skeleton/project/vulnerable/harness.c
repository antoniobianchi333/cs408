#include <stdio.h>
#include <unistd.h>

int main() {
    // NOTE: make sure the string ends with a NULL terminator
    char buf[4096] = {0};
    read(0, buf, sizeof(buf));
    buf[sizeof(buf)-1] = '\0';
    // TODO: call the vulnerable function
    return 0;
}