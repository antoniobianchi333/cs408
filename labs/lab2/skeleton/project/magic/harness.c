#include <stdio.h>
#include <unistd.h>

int main()
{
        char buf[4096] = {0};
        ssize_t len = read(0, buf, sizeof(buf));
        if (len < 0)
        {
                return 1;
        }

        // TODO: call the vulnerable function with buf and len

        return 0;
}
