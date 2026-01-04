//Deadlock attempt without actually freezing execution (spinlocks)

#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>

pthread_mutex_t lock;

void *fun1()
{
    int counter1 = 5;
    int got_lock = 0;
    while (counter1 > 0) {
        if (pthread_mutex_trylock(&lock) == 0) {
            // Failed to get lock
            got_lock = 1;
        }
        counter1--;
    }
    if (got_lock) {
        printf("No deadlock thread1\n");
    } else {
        printf("Deadlock thread1\n");
    }
    return NULL;
}

void *fun2()
{
    int counter2 = 5;
    int got_lock = 0;
    while (counter2 > 0) {
        if (pthread_mutex_trylock(&lock) == 0) {
            // Failed to get lock
            got_lock = 1;
        }
        counter2--;
    }
    if (got_lock) {
        printf("No deadlock thread2\n");
    } else {
        printf("Deadlock thread2\n");
    }
    return NULL;
}

int main()
{
    pthread_t thread1;
    pthread_t thread2;

    pthread_mutex_init(&lock, NULL);
    pthread_mutex_lock(&lock);

    pthread_create(&thread1, NULL, &fun1, NULL);
    pthread_create(&thread2, NULL, &fun2, NULL);

    return 0;
}