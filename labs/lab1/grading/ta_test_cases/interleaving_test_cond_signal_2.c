#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define N 4
#define N_LOCKS 1

/*
 * Without scheduling intervention this program will print 00000111112222233333
 * With random scheduling intervention this program will have a nondeterministic interleaving
 * Wit pct and proper seed, the output should be like 0123012301230123
 */

int count;
pthread_mutex_t locks[N_LOCKS];
pthread_cond_t cv1, cv2;
int finished = 0;
int helper_next = 0;
int iterations = 0;
int waiting = 0;
int func_call_var = 1;
int tcount = 0;

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
  pthread_mutex_lock(&locks[0]);
  int tid = tcount++;
  int tvar = func_call_var;
  func_call_var *= 8;
  pthread_mutex_unlock(&locks[0]);
  
  for(int i = 0; i < 5; i ++){
    usleep(tvar * 1000);
    pthread_mutex_lock(&locks[0]);
    waiting++;
    while (!helper_next)
      pthread_cond_wait(&cv1, &locks[0]);
    iterations++;
    helper_next = 1;
    //printf("in: %i\n", tvar);
    fprintf(stderr, "%i", tid);
    fflush(stderr);
    //printf("out: %i\n", tvar);
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
    int *arg = malloc(sizeof(*arg));
    if ( arg == NULL ) {
      fprintf(stderr, "Couldn't allocate memory for thread arg.\n");
      fflush(stderr);
      exit(EXIT_FAILURE);
    }

    *arg = id;
    pthread_create(&my_thread[id], NULL, worker_thread, arg);    
  }
  
  while (finished < N) {
    //printf("it:%i\n", iterations);
    if (waiting > 0) {
      pthread_mutex_lock(&locks[0]);
      helper_next = 1;
      waiting--;
      pthread_cond_signal(&cv1);
      pthread_mutex_unlock(&locks[0]);
    }
  }
  
  pthread_exit(NULL);
}
