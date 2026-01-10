int answer(int A, int B) {
    if (A > B) {    //  1
        A = A + 5;    //  2
        if (A >= 100) {    //  4
            A = A - 5;    //  5
            return A;
        }
    } else {
        A = B;    //  3
    }
    A = B + 5;    //  6
    return A;    //  7
}