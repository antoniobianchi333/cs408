#include <limits.h>
#include <stddef.h>

float _calculate_safe_average(int * data, int count, int * status) {
    // 1. Check status pointer validity first so we can report errors
    if (status == NULL) return 0.0f; 
    *status = 0; // Assume success initially

    // 1. Check array pointer validity & 2. Check for Division by Zero (count is 0)
    if (data == NULL || count <= 0) {
        *status = 1;
        return 0.0f;
    }

    int sum = 0;
    for (int i = 0; i < count; i++) {
        // 3. Check for Integer Overflow/Underflow
        if ((data[i] > 0 && sum > INT_MAX - data[i]) ||
            (data[i] < 0 && sum < INT_MIN - data[i])) {
            *status = 1;
            return 0.0f;
        }
        sum += data[i];
    }

    return (float)sum / count;
}