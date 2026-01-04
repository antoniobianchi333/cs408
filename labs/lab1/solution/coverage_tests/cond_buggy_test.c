#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

#define BUFFER_SIZE 10

char buffer[BUFFER_SIZE + 1];
pthread_mutex_t mutex;
pthread_cond_t condA;
pthread_cond_t condB;
int stop = 0;

int count = 0;

void *produce(void *arg)
{
    for (int i = 0; i < BUFFER_SIZE; i++) {
        pthread_mutex_lock(&mutex);
        while (count == BUFFER_SIZE) {
            pthread_cond_wait(&condB, &mutex);
        }
        buffer[i] = 'a' + (char)i;
        count++;
        pthread_cond_signal(&condA);
        pthread_mutex_unlock(&mutex);
        if (i == BUFFER_SIZE - 1) {
            stop = 1;
        }
    }
    pthread_exit(NULL);
}

void *consume(void *arg)
{
    for (int i = 0; i < BUFFER_SIZE; i++) {
        pthread_mutex_lock(&mutex);
        while (count == 0 && !stop) {
            pthread_cond_wait(&condA, &mutex);
        }
        if (stop && count == 0) {
            pthread_mutex_unlock(&mutex);
            break;
        }
        printf("Read %c from buffer[%d]\n", buffer[i], i);
        count--;
        pthread_cond_signal(&condB);
        pthread_mutex_unlock(&mutex);
    }
    pthread_exit(NULL);
}

int main()
{
    pthread_t thread1;
    pthread_t thread2;

    pthread_mutex_init(&mutex, NULL);
    pthread_cond_init(&condA, NULL);
    pthread_cond_init(&condB, NULL);

    for (int i = 0; i < BUFFER_SIZE; i++) {
        buffer[i] = ' ';
    }
    buffer[BUFFER_SIZE] = '\0';
    pthread_create(&thread1, NULL, &produce, NULL);
    pthread_create(&thread2, NULL, &consume, NULL);
    sleep(1);

    return 0;
}
