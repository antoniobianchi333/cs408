#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

volatile int shared_variable = 0;

void* foo(void * arg) {
    for (int i = 0; i < 10000; i++) {
        shared_variable++;
    }
    return (void*)0;
}

int main() {
  pthread_t thread1;
  pthread_t thread2;
  pthread_create(&thread1, NULL, &foo, NULL);
  pthread_create(&thread2, NULL, &foo, NULL);
  sleep(1);
  sleep(1);

  printf("%d\n", shared_variable);
  return 0;
}
