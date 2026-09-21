#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

/*
 * This test case is to check if pthread_mutex_lock and pthread_mutex_trylock is correctly implemented.
 * Outputs may differ according to scheduling policy and seed.
 * Check the order of each thread.
 */

pthread_t thread1;
pthread_t thread2;
pthread_mutex_t lock;

void* sample_func1(void* arg) {
    pthread_mutex_lock(&lock); 

    return NULL;
}

void* sample_func2(void* arg) {
    int x = pthread_mutex_trylock(&lock);

    if (x == EBUSY) {
        printf("** Trylock successfully returns EBUSY\n");
    } else {
        printf("** Error with Trylock\n");
    }
    return NULL;
}

int main(void) {
    pthread_mutex_init(&lock, NULL);
    pthread_create(&thread1, NULL, &sample_func1, NULL);
    pthread_create(&thread2, NULL, &sample_func2, NULL);

    pthread_exit(&thread1);
    pthread_exit(&thread2);
    pthread_mutex_destroy(&lock);
    return 0;
}
