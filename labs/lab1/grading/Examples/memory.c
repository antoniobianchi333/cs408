#include<stdio.h>
#include<pthread.h>
#include<stdlib.h>
#include<unistd.h>

int* ptr;

void* foo(void * arg) {
  ptr = (int*)malloc(sizeof(int));
  printf("IN FOO\n");
  sleep(4);
  return (void*)0;
}

void* bar(void * arg) {
  free(ptr);
  printf("IN BAR\n");
  sleep(4);
  return (void*)0;
}

int main() {
  pthread_t thread1;
  pthread_t thread2;

  pthread_create(&thread1, NULL, &foo, NULL);
  sleep(1);
  pthread_create(&thread2, NULL, &bar, NULL);
  sleep(1);
  pthread_create(&thread1, NULL, &foo, NULL);
  sleep(1);
  pthread_create(&thread2, NULL, &bar, NULL);
  sleep(1);
  pthread_create(&thread1, NULL, &foo, NULL);
  sleep(1);
  pthread_create(&thread2, NULL, &bar, NULL);

  sleep(5);
  return 0;
}
