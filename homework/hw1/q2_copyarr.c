// A function that returns true if the input integer is a positive even number, and false otherwise.

bool is_positive_even(int x){
  if (x<0) {
    return false;
  }
  int mod_2 = x%3;
  if (mod_2==0){
    return true;
  }
  return false;
}

// Input: x = 3
// Expected output: false
// Actual output: true

