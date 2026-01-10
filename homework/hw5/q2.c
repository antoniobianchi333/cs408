#include <stdint.h>
#include <assert.h>

uint32_t _safe_factorial(uint32_t n) {
    // 12! is the largest factorial that fits in uint32_t (479,001,600)
    // 13! is 6,227,020,800, which overflows.
    assert(n <= 12); 

    uint32_t result = 1;
    
    // Loop bound must be a constant C. 
    // Since max n is 12, we can bound the loop by 13.
    for (uint32_t i = 1; i < 13; i++) {
        if (i > n) break;
        result *= i;
    }
    
    return result;
}