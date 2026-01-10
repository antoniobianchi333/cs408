// Dividing two integers a and b and returning the result. 
// If b is 0, returning -1 to indicate error. 

int Divide(int a, int b){
    if(b==0){
        return -1;
    } else {
        return a/b;
    }
}