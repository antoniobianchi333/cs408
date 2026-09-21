#include <pthread.h>
#include <unistd.h>
#include <stdio.h>

/*
 * With no scheduling intervention, this program will output 1 2 3 4 5 6 7 8 9 10
 * With scheduling, the program might terminate early.
 */

pthread_mutex_t mutex;
int a = 0;

void *threadStuff() {
	sleep(1);
	pthread_mutex_lock(&mutex);
	a++;
	printf("** %d\n", a);
	pthread_mutex_unlock(&mutex);	
}

int main() {
	pthread_t threads[10];
	pthread_mutex_init(&mutex, NULL);
	for (int i = 0; i < 9; i++) {
		pthread_create(&threads[i], NULL, &threadStuff, NULL);
	}
	pthread_create(&threads[10], NULL, &threadStuff, NULL);
	sleep(5);
	return 0;
}
