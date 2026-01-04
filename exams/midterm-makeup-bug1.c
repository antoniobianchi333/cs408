int binarySearch(int *nums, unsigned int n, int target)
{
    // Assumes:
    //   nums is a valid pointer to an int array of size n
    //   entries in nums are ordered and all different
    //   n is smaller than 100
    // Effects:
    //   if target exists in array: return the position of `target` in array `nums` of size `n`
    //   otherwise: return -1
    int low = 1, high = n - 1;

    while (low <= high)
    {
        int mid = (low + high)/2;

        if (target == nums[mid]) {
            return mid;
        } else if (target < nums[mid]) {
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }

    return -1;
}
