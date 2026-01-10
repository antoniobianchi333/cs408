unsigned int fun(unsigned int a) {
  unsigned int res = 0;
  unsigned int i = 0;
  
  if(i < a) {
    res = res + i;
    i = i + 1;

    if(res == 3)
        return res;

    if(i < a) {
      res = res + i;
      i = i + 1;

      if(res == 3)
        return res;

      if(i < a) {
        res = res + i;
        i = i + 1;

        if(res == 3) {
          return res;
        }
        assert(!(i < a));
      }
    }
  }

  return res;
}