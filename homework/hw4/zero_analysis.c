int func() {
    double x = 10.0;
    int y = 5;
    int z = y;
    while (z > -1) {
        x = x / y;
        y = y + 1;
        z = z - 1;
    }
    int p = 10 / x;
    return p;
}
