#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#ifndef N
#define N 4
#endif

#ifndef N_LOCKS
#define N_LOCKS 2
#endif

int count;
pthread_mutex_t locks[N_LOCKS];

void init_locks() {
  for (int i=0; i < N_LOCKS; ++i) {
    if (pthread_mutex_init(&locks[i], NULL) != 0) { 
      fprintf(stderr, "\n mutex init has failed\n"); 
      fflush(stderr);
      exit(1); 
    } 
  }
}

void busy_lock(pthread_mutex_t* lock) {
  while (!pthread_mutex_trylock(lock)) {
    usleep(100);
  }
} 

void *worker_thread_even(void *arg)
{
  for(int i = 0; i < 10; i ++){
    for (int j = 0; j < N_LOCKS; ++j) {
      busy_lock(&locks[j]);
    }
    fprintf(stderr, "0");
    fflush(stderr);
    count = count + 1;
    usleep(1000);
    for (int j = N_LOCKS - 1; j >= 0; --j) {
      pthread_mutex_unlock(&locks[j]);
    }
    usleep(1000);
  }
  pthread_exit(NULL);
}

void *worker_thread_odd(void *arg)
{
  for(int i = 0; i < 10; i ++){
    for (int j = N_LOCKS - 1; j >= 0; --j) {
      busy_lock(&locks[j]);
    }
    fprintf(stderr, "1");
    fflush(stderr);
    count = count + 1;
    usleep(100);
    for (int j = 0; j < N_LOCKS; ++j) {
      pthread_mutex_unlock(&locks[j]);
    }
    usleep(1000);
  }
  pthread_exit(NULL);
}

int main()
{
  pthread_t my_thread[N];
  init_locks();
  count = 0;
  
  for(long id = 1; id <= N; ++id) {
    if (id & 0x1) {
      pthread_create(&my_thread[id], NULL, worker_thread_odd, (void*)id);    
    }
    else {
      pthread_create(&my_thread[id], NULL, worker_thread_even, (void*)id);    
    }
  }
  
  pthread_exit(NULL);
}
