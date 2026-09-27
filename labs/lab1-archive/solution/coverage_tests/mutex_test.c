#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void *foo(void *arg)
{
    pthread_mutex_lock(&mutex);
    printf("Mutex acquired\n");
    pthread_mutex_unlock(&mutex);
    return (void *)0;
}

int main()
{
    pthread_t thread1;
    pthread_t thread2;
    pthread_mutex_init(&mutex, NULL);

    pthread_mutex_lock(&mutex);

    pthread_create(&thread1, NULL, &foo, NULL);
    sleep(1);

    pthread_mutex_unlock(&mutex);

    sleep(1);
    sleep(1);

    return 0;
}
