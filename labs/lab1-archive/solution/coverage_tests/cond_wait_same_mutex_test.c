#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

int shared_variable = 0;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;

void *signal(void *arg)
{
    for (int i = 0; i < 10; i++) {
        pthread_mutex_lock(&mutex);
        pthread_cond_signal(&cond);
        pthread_mutex_unlock(&mutex);
        sleep(1);
    }
    return (void *)0;
}

void *wait(void *arg)
{
    for (int i = 0; i < 10; i++) {
        pthread_mutex_lock(&mutex);
        pthread_cond_wait(&cond, &mutex);
        pthread_mutex_unlock(&mutex);
    }
    return (void *)0;
}

int main()
{
    pthread_t signal_thread;
    pthread_t wait_thread;

    pthread_mutex_init(&mutex, NULL);
    pthread_cond_init(&cond, NULL);

    pthread_create(&wait_thread, NULL, &wait, NULL);
    sleep(1);
    pthread_create(&signal_thread, NULL, &signal, NULL);
    sleep(1);
    sleep(1);

    return 0;
}
