#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define BUFFER_SIZE 10
#define NUM_THREADS 2

char buffer[BUFFER_SIZE + 1];

void *produce(void *arg)
{
    for (int i = 0; i < BUFFER_SIZE; i++) {
        buffer[i] = 'a' + (char)i;
        printf("Wrote %c to buffer[%d]\n", buffer[i], i);
    }
    pthread_exit(NULL);
}

void *consume(void *arg)
{
    for (int i = 0; i < BUFFER_SIZE; i++) {
        printf("Read %c from buffer[%d]\n", buffer[i], i);
    }
    pthread_exit(NULL);
}

int main()
{
    pthread_t thread1;
    pthread_t thread2;

    for (int i = 0; i < BUFFER_SIZE; i++) {
        buffer[i] = ' ';
    }
    buffer[BUFFER_SIZE] = '\0';
    pthread_create(&thread1, NULL, &produce, NULL);
    pthread_create(&thread2, NULL, &consume, NULL);

    sleep(1);
    printf("Buffer: %s\n", buffer);

    return 0;
}
