#include <stdio.h>
#include <pthread.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>

int string_equal(const char *str1, const char *str2)
{
    return strcmp(str1, str2) == 0;
}

int get_algorithm_ID()
{
    char *algorithm_var = getenv("ALGORITHM");
    if (string_equal(algorithm_var, "pct"))
        return 1;
    return 0;
}

int main()
{
    if (get_algorithm_ID()) {
        pthread_cond_t cond;
        pthread_mutex_t mutex;
        pthread_cond_init(&cond, NULL);
        pthread_mutex_init(&mutex, NULL);
        pthread_cond_wait(&cond, &mutex);
    }
    return 0;
}
