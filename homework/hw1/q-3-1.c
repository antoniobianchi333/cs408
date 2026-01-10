void function(int a, int b) {
    while (a < 5) { // node 1
        if (b > 5) { // node 2
            continue;
        }
        a = 5 // node 3
        return; // node 4
    }
    a = 0; // node 5
    b = 0; // node 6
    return; // node 4
}

