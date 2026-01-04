#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <stdlib.h>

volatile int flag = 0;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void* foo(void * arg) {
  pthread_mutex_lock(&mutex);
  if (flag) {
    pthread_mutex_unlock(&mutex);
    volatile int *arr = malloc(sizeof(int) * 10);
    arr[0] = 1;
  } else {
    pthread_mutex_unlock(&mutex);
  }
  return (void*)0;
}

int main() {
  pthread_t thread1;
  pthread_mutex_init(&mutex, NULL);

  pthread_create(&thread1, NULL, &foo, NULL);
  pthread_mutex_lock(&mutex);
  flag = 1;
  pthread_mutex_unlock(&mutex);
  sleep(1);

  return 0;
}