#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define N 4
#define N_LOCKS 1

/*
 * Without scheduling intervention this program will print the thread indexes in arbitrary order each time.
 * With pct and a proper seed, this program should print the indexes in the same order repeatedly.
 */

int count;
pthread_mutex_t locks[N_LOCKS];
pthread_cond_t cv1;
int finished = 0;
int helper_next = 0;
int waiting = 0;

void init_locks() {
  for (int i=0; i < N_LOCKS; ++i) {
    if (pthread_mutex_init(&locks[i], NULL) != 0) { 
      printf("\n mutex init has failed\n"); 
      fflush(stderr);
      exit(1); 
    } 
  }
}

void *worker_thread(void *arg)
{
  //printf("%i", *(int*)arg);
  for(int i = 0; i < 10; i ++){
    pthread_mutex_lock(&locks[0]);
    waiting++;
    pthread_cond_wait(&cv1, &locks[0]);
    fprintf(stderr, "%d", gettid() % 10);
    fflush(stderr);
    pthread_mutex_unlock(&locks[0]);
  }
  
  pthread_mutex_lock(&locks[0]);
  finished++;
  pthread_mutex_unlock(&locks[0]);
  pthread_exit(NULL);
}

int main()
{
  pthread_t my_thread[N];
  pthread_cond_init(&cv1, NULL);
  init_locks();
  count = 0;
  
  for(int id = 0; id < N; ++id) {
    pthread_create(&my_thread[id], NULL, worker_thread, NULL);    
  }
  
  while (finished < N) {
    pthread_mutex_lock(&locks[0]);
    if (waiting + finished >= N) {
      fprintf(stderr, " ");
      fflush(stderr);
      waiting = 0;
      pthread_cond_broadcast(&cv1);
    }
    pthread_mutex_unlock(&locks[0]);
  }
  
  pthread_exit(NULL);
}
