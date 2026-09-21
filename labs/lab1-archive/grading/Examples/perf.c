#include<stdio.h>
#include<pthread.h>
#include<unistd.h>

int main() {
  printf("Start of perf.c\n");
  sleep(11);
  printf("End of perf.c\n");
  return 0;
}
