#define _GNU_SOURCE

#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define N 3
#define N_LOCKS 1

/*
 * Without scheduling intervention this program will have nondeterministical output
 * With pct this program will output sequences of identical values (eg: 111111111111111111112222222222222222222200000000000000000000)
 */

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

void *worker_thread(void *arg)
{
  for(int i = 0; i < 20; i ++){
    fprintf(stderr, "%d", gettid() % 10);
    fflush(stderr);
    pthread_yield();
  }
  pthread_exit(NULL);
}

int main()
{
  pthread_t my_thread[N];
  
  init_locks();
  count = 0;
  
  for(int id = 0; id < N; ++id) {
    pthread_create(&my_thread[id], NULL, worker_thread, NULL);    
  }
  
  pthread_exit(NULL);
}
