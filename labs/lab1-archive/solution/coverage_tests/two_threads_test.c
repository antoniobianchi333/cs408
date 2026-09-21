#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

void *foo(void *arg)
{
    int x = 3;
    x += 1;
    return (void *)0;
}

int main()
{
    pthread_t thread1;
    pthread_t thread2;
    pthread_create(&thread1, NULL, &foo, NULL);
    pthread_create(&thread2, NULL, &foo, NULL);
    sleep(1);
    return 0;
}
