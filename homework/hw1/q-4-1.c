void abs(int a) {
  result = 0;
  if (a < 0) {  // Node 1 (line2-3)
    result = -a;  // Node 2
  } else {
    result = a;  // Node 3
  }
  return result; // Node 4
}