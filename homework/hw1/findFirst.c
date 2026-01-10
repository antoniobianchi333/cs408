// Effects: If x == null throw NullPointerException
// Else return the index of the first element in x that equals y.
// If no such element exists, return -1
public int findFirst(int[] x, int y) // 1
    for (int i = 0; i < x.length - 1; i++) // 2
    {
        if (x[i] == y) // 3
        {
            return i; // 4
        }
    }
    return -1; // 5
    }
    // test x=[2, 3, 5]; y = 5; // 6
    // Expected result = 2 // 7