while (low <= high) { // 1​
	int middle = low + (high - low) / 2;​ // 2
	if (target < a[middle])​ // 3
		high = middle - 1; // 4​
	else if (target > a[middle])​ // 5
		low = middle + 1;  else​ // 6
	else { // 7
		return middle; // 8
	} // 9

return -1 // Target not found in a[low,  high] // 10