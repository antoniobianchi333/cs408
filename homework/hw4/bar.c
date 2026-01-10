#include <stdio.h>
#include <math.h>
double bar(double x, double y, double a, double b) {
    double result;
    // Program state?
    if (x == y && b > 0) {
        result = (3 * x) / (b - a);   // FP Div
    } else {
        x = fmax(x , a);
        a += b;
        if (x <= 0) {
            a = a * 3;
            // Program state?
        }
        y = y / 5;   // FP Div
        result = x + y + a + 1;
    }
    // Program state?
    return result;
}
