#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define N 2
#define N_LOCKS 1

/*
 * Without scheduling intervention this program will almost deterministically output 12121212121212121212
 * With random scheduling this program will have slight deviations from that.
 * With pct this program will output sequences of identical values (eg: 111111222222)
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

void *worker_thread1(void *arg)
{
  for(int i = 0; i < 20; i ++){
    for (int j = 0; j < N_LOCKS; ++j) {
      pthread_mutex_lock(&locks[j]);
    }

    count = count + 1;
    fprintf(stderr, "1");
    fflush(stderr);
    usleep(2000);
    for (int j = N_LOCKS - 1; j >= 0; --j) {
      pthread_mutex_unlock(&locks[j]);
    }
    usleep(2000);
  }
  pthread_exit(NULL);
}

void *worker_thread2(void *arg)
{
  for(int i = 0; i < 20; i ++){
    for (int j = 0; j < N_LOCKS; ++j) {
      pthread_mutex_lock(&locks[j]);
    }

    count = count + 1;
    fprintf(stderr, "2");
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
      pthread_create(&my_thread[id], NULL, worker_thread1, NULL);
    } else {
      pthread_create(&my_thread[id], NULL, worker_thread2, NULL);
    }
  }
  
  pthread_exit(NULL);
}
