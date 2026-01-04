#include<stdio.h>
#include<pthread.h>
#include<unistd.h>

int x;

void* foo(void * arg) {
  for (int i = 0; i < 1000; i++) {
    x++;
  }
  return (void*)0;
}

int main() {
  x = 0;
  pthread_t thread1;
  pthread_t thread2;
  pthread_create(&thread1, NULL, &foo, NULL);
  pthread_create(&thread2, NULL, &foo, NULL);
  sleep(1);
  printf("The value of x is: %d\n", x);
  pthread_detach(thread1);
  pthread_detach(thread2);
  return 0;
}
