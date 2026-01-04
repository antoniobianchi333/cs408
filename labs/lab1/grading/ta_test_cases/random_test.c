#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#ifndef N
#define N 2
#endif

#ifndef N_LOCKS
#define N_LOCKS 1
#endif

/*
 * Without scheduling intervention this program will almost deterministically output 0101010101010101010101010101010101010101
 * With random scheduling the output will differ slightly from without itervention
 * With pct this program will output either 1111111111111111111100000000000000000000 or the reverse
 */

int count;

int file_write(int num){
    FILE *fp;
    fp = fopen("output.txt", "a+");
    if (fp == NULL) {
        fprintf(stderr, "Error opening file.\n");
        return 1;
    }
    fprintf(fp, "%d", num);
    fclose(fp);
    return 0;
}
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

void *worker_thread_even(void *arg)
{
  for(int i = 0; i < 20; i ++){
    for (int j = 0; j < N_LOCKS; ++j) {
      pthread_mutex_lock(&locks[j]);
    }

    count = count + 1;
    // fprintf(stderr, "%d", 1);
    file_write(1);
    fflush(stderr);
    usleep(2000);
    for (int j = N_LOCKS - 1; j >= 0; --j) {
      pthread_mutex_unlock(&locks[j]);
    }
    usleep(2000);
  }
  pthread_exit(NULL);
}

void *worker_thread_odd(void *arg)
{
  for(int i = 0; i < 20; i ++){
    for (int j = 0; j < N_LOCKS; ++j) {
      pthread_mutex_lock(&locks[j]);
    }

    count = count + 1;
    // fprintf(stderr, "%d", 0);
    file_write(0);
    fflush(stderr);
    usleep(2000);
    for (int j = N_LOCKS - 1; j >= 0; --j) {
      pthread_mutex_unlock(&locks[j]);
    }
    usleep(2000);
  }
  pthread_exit(NULL);
}

int main()
{
  pthread_t my_thread[N];
  init_locks();
  count = 0;
  
  for(int id = 0; id < N; ++id) {
    if (id & 0x1) {
      pthread_create(&my_thread[id], NULL, worker_thread_odd, NULL);
    } else {
      pthread_create(&my_thread[id], NULL, worker_thread_even, NULL);
    }
    
  }
  usleep(2000);
  FILE *fp;
  fp = fopen("output.txt", "a+");
  if (fp == NULL) {
  fprintf(stderr, "Error opening file.\n");
    return 1;
  }
  fprintf(fp, "\n");
  fclose(fp);
  
  pthread_exit(NULL);
}
