#include <pthread.h>
#include <stdio.h>

int x = 0;

void *Worker(void *_)
{
    x = 42; // W(x), no lock
    return NULL;
}

int main()
{
    pthread_t t;
    pthread_create(&t, NULL, Worker, NULL); // fork
    pthread_join(t, NULL);                  // join
    printf("%d\n", x);                      // R(x), no lock
    return 0;
}