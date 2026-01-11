int bof(unsigned long i, int b[20]) {
    if (i == 0xDEAD0DEAD)
        return b[i];
    return 0;
}
