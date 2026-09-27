#define _GNU_SOURCE
#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *foo(void *arg)
{
    printf("Thread %ld started\n", (long)arg);
    pthread_yield();
    printf("Thread %ld resumed\n", (long)arg);
    pthread_exit(NULL);
    return (void *)0;
}

int main()
{
    pthread_t thread1;
    pthread_t thread2;

    pthread_create(&thread1, NULL, &foo, (void *)1);
    pthread_create(&thread2, NULL, &foo, (void *)2);
    sleep(1);
    return 0;
}
