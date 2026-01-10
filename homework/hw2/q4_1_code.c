#include <pthread.h>

int x = 0;
pthread_mutex_t A = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t B = PTHREAD_MUTEX_INITIALIZER;

void* T1(void* _) {
    pthread_mutex_lock(&A);    // L(A)
    x++;                       // W(x)
    pthread_mutex_unlock(&A);  // U(A)
    return NULL;
}

void* T2(void* _) {
    x++;                       // W(x)
    return NULL;
}

int main() {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, T1, NULL);
    pthread_create(&t2, NULL, T2, NULL);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    return 0;
}