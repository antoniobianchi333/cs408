#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#ifndef N
#define N 10
#endif

#ifndef N_LOCKS
#define N_LOCKS 10
#endif

/*
 * Sanity test to ensure PCT does not detect any deadlock
 */

int count;
pthread_mutex_t locks[N_LOCKS];

void init_locks() {
  for (int i=0; i < N_LOCKS; ++i) {
    if (pthread_mutex_init(&locks[i], NULL) != 0) { 
      printf("\n mutex init has failed\n"); 
      exit(1); 
    } 
  }
}

void *worker_thread(void *arg)
{
  for(int i = 0; i < 1000; i ++){
    for (int j = 0; j < N_LOCKS; ++j) {
      pthread_mutex_lock(&locks[j]);
    }

    count = count + 1;
    for (int j = N_LOCKS - 1; j >= 0; --j) {
      pthread_mutex_unlock(&locks[j]);
    }
  }
  pthread_exit(NULL);
}

int main()
{
  pthread_t my_thread[N];
  init_locks();
  count = 0;
  
  for(int id = 0; id < N; ++id) {
    int *arg = malloc(sizeof(*arg));
    if ( arg == NULL ) {
      fprintf(stderr, "Couldn't allocate memory for thread arg.\n");
      exit(EXIT_FAILURE);
    }

    *arg = id;
    pthread_create(&my_thread[id], NULL, worker_thread, arg);    
  }
  
  pthread_exit(NULL);
}
