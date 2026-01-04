#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define NUM_THREADS 15

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;

void *foo(void *thread_id)
{
    int tid = *(int *)thread_id;

    printf("Thread %d started\n", tid + 1);
    pthread_mutex_lock(&mutex);

    printf("Thread %d waiting\n", tid + 1);
    pthread_cond_wait(&cond, &mutex);

    printf("Thread %d continuing\n", tid + 1);
    pthread_mutex_unlock(&mutex);

    return NULL;
}

int main()
{
    pthread_t threads[NUM_THREADS];
    int thread_ids[NUM_THREADS];

    pthread_mutex_init(&mutex, NULL);
    pthread_cond_init(&cond, NULL);

    for (int i = 0; i < NUM_THREADS; i++) {
        thread_ids[i] = i;
        if (pthread_create(&threads[i], NULL, &foo, &thread_ids[i])) {
            fprintf(stderr, "Error creating thread %d\n", i);
            exit(-1);
        }
    }

    sleep(1);
    sleep(1);

    printf("Broadcast\n");
    pthread_cond_broadcast(&cond);

    sleep(1);
    sleep(1);

    return 0;
}
