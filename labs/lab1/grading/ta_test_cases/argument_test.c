#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define N 2
#define N_LOCKS 1

/*
 * Check if the arguments of the start_routine is handled correctly
 */

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
  fprintf(stderr, "%i", *(int*)arg);
  fflush(stderr);
  pthread_exit(NULL);
}

int main()
{
  pthread_t my_thread[N];
  init_locks();
  
  for(int id = 1; id <= N; ++id) {
    int *arg = malloc(sizeof(*arg));
    if ( arg == NULL ) {
      fprintf(stderr, "Couldn't allocate memory for thread arg.\n");
      fflush(stderr);
      exit(EXIT_FAILURE);
    }
    *arg = id;
    pthread_create(&my_thread[id], NULL, worker_thread, arg);    
  }
  
  pthread_exit(NULL);
}
