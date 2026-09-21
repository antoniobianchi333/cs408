#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

void vulnerable_function(const char *input, size_t len)
{
    if (len < 15)
        return;

    uint32_t val1 = *(uint32_t *)&input[0];

    // Layer 1: Check for "MAGI" + 'C'
    if (val1 == 0x4947414D && input[4] == 'C')
    {
        fprintf(stderr, "Layer 1 passed\n");

        // Layer 2: Check for "2025"
        uint32_t val2 = *(uint32_t *)&input[5];
        if (val2 == 0x35323032)
        {
            fprintf(stderr, "Layer 2 passed\n");

            // Layer 3: Check for "X9Y7"
            uint32_t val3 = *(uint32_t *)&input[9];
            if (val3 == 0x37593958)
            {
                fprintf(stderr, "Layer 3 passed\n");

                uint16_t val4 = *(uint16_t *)&input[13];
                // Layer 4: Check for "OK"
                if (val4 == 0x4B4F)
                {
                    fprintf(stderr, "Layer 4 passed - CRASH!\n");
                    int *crash = NULL;
                    *crash = 42;
                }
            }
        }
    }
}
