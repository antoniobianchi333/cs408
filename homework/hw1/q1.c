int partition (int arr[], int low, int high)
{
    int pivot = arr[high];  //1
    int i = (low - 1);      //1

    for (int j = low;       //1
         j <= high - 1;     //2
         j++)               //3
    {
        // If current element is smaller than the pivot
        if (arr[j] < pivot) //4
        {
            i++; // increment index of smaller element  //5
            swap(&arr[i], &arr[j]);                     //5
        }
    }
    swap(&arr[i + 1], &arr[high]);  //6
    return (i + 1);                 //6
}
