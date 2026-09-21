#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define ARRAY_SIZE 10

int array[ARRAY_SIZE];

void *consume()
{
    for (int i = 0; i < ARRAY_SIZE; i++) {
        printf("Read %d: array[%d] = %d\n", 2, i, array[i]);
    }
    // pthread_exit(NULL);
    return NULL;
}

void *produce()
{
    for (int i = 0; i < ARRAY_SIZE; i++) {
        array[i] = i + 1;
    }
    // pthread_exit(NULL);
    return NULL;
}

int main()
{
    pthread_t thread1;
    pthread_t thread2;
    for (int i = 0; i < ARRAY_SIZE; i++) {
        array[i] = 0;
    }

    pthread_create(&thread1, NULL, &produce, NULL);
    pthread_create(&thread2, NULL, &consume, NULL);

    sleep(1);

    return 0;
}