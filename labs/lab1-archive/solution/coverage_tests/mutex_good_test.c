#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <assert.h>

int shared_variable = 0;
pthread_mutex_t mutex;

void *foo(void *arg)
{
    for (int i = 0; i < 5; i++) {
        pthread_mutex_lock(&mutex);
        shared_variable++;
        pthread_mutex_unlock(&mutex);
    }
    pthread_exit(1);
}

int main()
{
    pthread_t thread1;
    pthread_t thread2;
    pthread_mutex_init(&mutex, NULL);
    pthread_create(&thread1, NULL, &foo, NULL);
    pthread_create(&thread2, NULL, &foo, NULL);
    sleep(1);
    // assert(shared_variable == 10);
    printf("Shared_variable: %d\n", shared_variable);
    return 0;
}
