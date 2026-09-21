#include <stdio.h>
#include <pthread.h>
#include <stdlib.h>

volatile int crash_var = 0;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void *foo(void *arg)
{
    crash_var = 1;
    return (void *)0;
}

int main()
{
    pthread_t thread;
    pthread_mutex_init(&mutex, NULL);

    pthread_create(&thread, NULL, &foo, NULL);

    pthread_mutex_lock(&mutex);
    if (crash_var) {
        pthread_mutex_unlock(&mutex);
        *((char *)-1) = 'x';
    } else {
        sleep(1);
    }
    pthread_mutex_unlock(&mutex);

    return 0;
}