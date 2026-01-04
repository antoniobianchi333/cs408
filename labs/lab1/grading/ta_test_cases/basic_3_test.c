#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdbool.h>
#include <assert.h>

#define NUM_TO_TEST 2

/*
 * This function is to check coditional variable functions.
 * Output may differ according to scheduling policy and seed.
 */


// simulate a producer-consumer
bool buffer_used = false;  // buffer of size 1
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;

void* produce(void * arg) {
    for (int i = 0; i < NUM_TO_TEST; i++) {
        pthread_mutex_lock(&mutex);

        while (buffer_used) {
		printf("** (p) buffer used, wait for condition\n");
		pthread_cond_wait(&cond, &mutex);
        }

        buffer_used = true;
        printf("** (p) broadcast\n");
        pthread_cond_broadcast(&cond);
        pthread_mutex_unlock(&mutex);
    }
    return (void*)0;
}

void* consume(void * arg) {
    for (int i = 0; i < NUM_TO_TEST; i++) {
        pthread_mutex_lock(&mutex);

        while (!buffer_used) {
		printf("** (c) buffer not used, wait for condition\n");
		pthread_cond_wait(&cond, &mutex);
        }

        buffer_used = false;
        pthread_cond_signal(&cond);
	printf("** (c) signal\n");
        pthread_mutex_unlock(&mutex);
    }
    return (void*)0;
}

int main() {
    pthread_t thread1;
    pthread_t thread2;
    pthread_create(&thread1, NULL, &produce, NULL);
    pthread_create(&thread2, NULL, &consume, NULL);

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    assert(buffer_used == false);
    return 0;
}
