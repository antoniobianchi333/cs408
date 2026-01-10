void insertionSort(int a[], int n)
{
    int i, loc, j, k, selected; // 1
  
    for (i = 1; i < n; ++i) // 2
    {
        j = i - 1; // 3
        selected = a[i]; // 3
  
        loc = binarySearch(a, selected, 0, j); // 4
  
        while (j >= loc) // 5
        {
            a[j + 1] = a[j]; // 6
            j--; // 6
        }
        a[j + 1] = selected; // 7
    }

   return; // 8
}