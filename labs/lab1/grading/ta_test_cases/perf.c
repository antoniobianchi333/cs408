#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <stdint.h>
#include <string.h>

#define HANG_PROB 0.1

volatile float rand_prob = 1.0;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void* foo(void *arg) {
    if (pthread_mutex_trylock(&mutex) == 0) {
        rand_prob = (float)rand() / RAND_MAX;
        pthread_mutex_unlock(&mutex);
    }
    return NULL;
}

// We generate a seed based on the SEED environment variable
uint64_t get_seed() {
  char * seed_var = getenv("SEED");
  return strtoull(seed_var,NULL,10);
}

int main() {
    pthread_t thread;
    pthread_mutex_init(&mutex, NULL);

    pthread_create(&thread, NULL, &foo, NULL);

    volatile int hang = 0;
    pthread_mutex_lock(&mutex);
    if (rand_prob < HANG_PROB || get_seed() > 13) {
        hang = 1;
    }
    pthread_mutex_unlock(&mutex);

    if (hang) {
        sleep(3 * get_seed());
    }

    sleep(1);

    return 0;
}
