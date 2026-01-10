void q4_answer(int a, int b)
{
  a = a + b; //1
  int i=0; //1
  while (i < b) //2
  {
    a = a + i; //3
    while (b > 0) //4
    {
      if (a > b) //5
      {
        a = a - b; //6
      }
      a++; //7
    }
    b++; //8
    i++; //8
  }
  return; //9
}
  
