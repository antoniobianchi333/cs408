#include<stdio.h>
#include<pthread.h>
#include<unistd.h>

int *p;

void* foo1(void * arg) {
  sleep(1);
  *p = NULL;
  return (void*)0;
}

void* foo2(void * arg) {
  fprintf("This int probably won't print: %d\n", *p);
  return (void*)0;
}

int main() {
  pthread_t thread1, thread2;
  *p = 5;
  pthread_create(&thread1, NULL, &foo1, NULL);
  pthread_create(&thread2, NULL, &foo2, NULL);
  sleep(2);
  pthread_detach(thread1);
  pthread_detach(thread2);
  return 0;
}
