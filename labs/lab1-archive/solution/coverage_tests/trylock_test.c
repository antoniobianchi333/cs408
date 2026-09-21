#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <assert.h>

int shared_variable = 0;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void *foo(void *arg)
{
    int res = pthread_mutex_trylock(&mutex);
    if (res == 0) {
        printf("Thread %ld acquired mutex\n", (long)arg);
        shared_variable++;
        pthread_mutex_unlock(&mutex);
    } else {
        printf("Thread %ld failed to acquire mutex\n", (long)arg);
    }

    return (void *)0;
}

int main()
{
    pthread_t thread1;
    pthread_t thread2;
    pthread_mutex_init(&mutex, NULL);
    pthread_create(&thread1, NULL, &foo, (void *)1);
    pthread_create(&thread2, NULL, &foo, (void *)2);
    sleep(1);
    printf("%d\n", shared_variable);
    return 0;
}
