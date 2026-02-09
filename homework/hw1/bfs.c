// this little program can be used to validate students' test cases/outputs

#include <stdio.h>
#include <string.h>

#define MAX 20

#define Println(x) println(x, &counter)

int* bfs(int graph[MAX][MAX], int start, int visited[], int n, int *size);

int main() {

  int graph[MAX][MAX]; //malloc(MAX * MAX * sizeof(int));
  memset(graph, 0, MAX * MAX * sizeof(int));

//  graph[0][0] = 1;
//  graph[0][1] = 1;
//  graph[1][0] = 1;
//  graph[1][1] = 1;  

//  graph[0][2] = 1;
//  graph[1][2] = 1;
//  graph[2][0] = 1;
//  graph[2][1] = 1;

  int start = 0;
  int visited[MAX];
  memset(visited, 0, MAX * sizeof(int));

//  visited[0] = 1;


  int n = 20;
  int size = 0;

  bfs(graph, start, visited, n, &size);
  
//  free(graph);

}




void println(int i, int* counter) {
  printf("%d,  %d\n", i, *counter);
  *counter = *counter + 1;
}




int* bfs(int graph[MAX][MAX], int start, int visited[], int n, int *size) 
{ 
  int counter = 0;
  Println(1);
  static int order[MAX]; //1
  int queue[MAX], front = 0, end = 0, i; // 1
  int k = 0; // 1
  
  queue[end++] = start; //1
  visited[start] = 1; //1
  
  Println(2);
  for (front = 0; front<end; front++) // 2
  { 
    Println(3);
    int node = queue[front]; // 3
    order[k++] = node; //3

    i = 0; // 3

    Println(4);
    while(i<n) // 4
    { 
      Println(5);
      if(graph[node][i] == 1 && !visited[i]) // 5
      { 
        Println(6);
        queue[end++] = i; // 6
        visited[i] = 1; // 6
      } 

      Println(7);
      i++; // 7
      Println(4);
    } 
    Println(2);
  } 
  Println(8);
  *size = k; //8
  Println(9);
  return order; // 9
}


