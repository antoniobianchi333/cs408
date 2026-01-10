#define MAX 20
int* bfs(int graph[MAX][MAX], int start, int visited[], int n, int *size) 
{ 
  static int order[MAX]; //1
  int queue[MAX], front = 0, end = 0, i; // 1
  int k = 0; // 1
  
  queue[end++] = start; //1
  visited[start] = 1; //1
  for (front = 0; front<end; front++) // 2
  { 
    int node = queue[front]; // 3
    order[k++] = node; //3

    i = 0; // 3

    while(i<n) // 4
    { 
      if(graph[node][i] == 1 && !visited[i]) // 5
      { 
        queue[end++] = i; // 6
        visited[i] = 1; // 6
      } 
      i++; // 7
    } 
  } 
  *size = k; //8
  return order; // 9
}