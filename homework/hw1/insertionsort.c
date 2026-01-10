void insertionSort(int a[], int n)
{
    int i, loc, j, k, selected;
  
    for (i = 1; i < n; ++i) 
    {
        j = i - 1;
        selected = a[i];
  
        // find location where selected should be inseretd
        loc = binarySearch(a, selected, 0, j);
  
        // Move all elements after location to create space
        while (j >= loc) 
        {
            a[j + 1] = a[j];
            j--;
        }
        a[j + 1] = selected;
    }

    return;
}