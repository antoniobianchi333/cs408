#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <assert.h>

int shared_variable = 0;
pthread_mutex_t mutex;

void *foo(void *arg)
{
    for (int i = 0; i < 10000; i++) {
        // FIXME: mutex_lock
        shared_variable++;
        // FIXME: mutex_unlock
    }
    return (void *)0;
}

int main()
{
    pthread_t thread1;
    pthread_t thread2;
    pthread_create(&thread1, NULL, &foo, NULL);
    pthread_create(&thread2, NULL, &foo, NULL);

    sleep(1);
    printf("Shared_variable: %d\n", shared_variable);
    return 0;
}
