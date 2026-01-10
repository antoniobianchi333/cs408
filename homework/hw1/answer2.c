int answer(int A, int B) {
    if(A) { // 1
        if(B) { // 3
            goto label; // 5
        }
    }
    else {
        // 2
    }
    // 4
    label: return A; // 6
}