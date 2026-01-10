void fun(int a, int b, int c) {
  int x = 100;

  if(a >= 0) {
    x = 50;
  }
  
  if(b + c > 0) {
    x += c;

    if(x < 70) {
      x += a;
    }
  }
}