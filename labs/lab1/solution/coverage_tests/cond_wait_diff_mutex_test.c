#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

int shared_variable = 0;
pthread_mutex_t mutex[2];
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;

void *wait(void *arg)
{
    pthread_mutex_lock(&mutex[0]);
    pthread_cond_wait(&cond, &mutex[0]);
    pthread_mutex_unlock(&mutex[0]);
    return (void *)0;
}

void *wait2(void *arg)
{
    pthread_mutex_lock(&mutex[1]);
    pthread_cond_wait(&cond, &mutex[1]);
    pthread_mutex_unlock(&mutex[1]);
    return (void *)0;
}

int main()
{
    pthread_t wait_thread;
    pthread_t wait2_thread;

    pthread_mutex_init(&mutex[0], NULL);
    pthread_mutex_init(&mutex[1], NULL);
    pthread_cond_init(&cond, NULL);

    pthread_create(&wait_thread, NULL, &wait, NULL);
    pthread_create(&wait2_thread, NULL, &wait2, NULL);

    sleep(1);
    sleep(1);
    sleep(1);
    sleep(1);

    return 0;
}
