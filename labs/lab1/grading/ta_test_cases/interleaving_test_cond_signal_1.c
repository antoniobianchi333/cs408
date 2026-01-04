#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>


#define N 2
#define N_LOCKS 1

/*
 * Without scheduling intervention this program will have a fairly random sequence output.
 * With pct and proper seed this program will output sequences of alternating values (eg: 0101010101010101010101010101010101010101)
 */

int count;
pthread_mutex_t locks[N_LOCKS];
pthread_cond_t cv1, cv2;
int finished = 0;
int helper_next = 0;
int iterations = 0;

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
    pthread_mutex_lock(&locks[0]);
    while (!helper_next)
      pthread_cond_wait(&cv1, &locks[0]);
    helper_next = 0;
    iterations++;
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
  pthread_cond_init(&cv2, NULL);
  init_locks();
  count = 0;
  
  for(int id = 0; id < N; ++id) {
    pthread_create(&my_thread[id], NULL, worker_thread, NULL);    
  }
  
  while (finished < N) {
    pthread_mutex_lock(&locks[0]);
    //printf("Main thread loop entered %i\n", iterations);
    helper_next = 1;
    pthread_cond_signal(&cv1);
    pthread_mutex_unlock(&locks[0]);
  }
  
  pthread_exit(NULL);
}
