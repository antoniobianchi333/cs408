/* Define the node */
typedef struct Node {
    int data;
    struct Node* next;
} Node;


/* Returns the number of items, up to 10 */
void count_up_to_10(Node* head) {
    Node* curr = head;
    int cnt = 0;
    while (curr && cnt < 10) {
        curr = curr->next;
        cnt++;
    }
    return cnt;
}


