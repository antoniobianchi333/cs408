package lec2examples;

/**
 * Hello world!
 */
public final class App {
    private App() {
    }

    public static int numZero(int[] x) {
        // Effects: if x==null throw NullPointerException
        // else return the number of occurrences of 0 in x
        int count = 0;
        for (int i = 0; i < x.length; i++) {
            if (x[i] == 0) {
                count++;
            }
        }
        return count;
    }

    public int findLast(int[] x, int y) {
        // Effects: if x==null throw NullPointerException
        // else return the index of the last element
        // in x that equals y.
        // If no such element exists, return -1.

        for (int i = x.length - 1; i > 0; i--) {
            if (x[i] == y) {
                return i;
            }
        }
        return -1;
    }
    // Test: x=[2,3,5]; y=2
    // Expected result = 0

int index_even(unsigned int* x, unsigned int len, int n){
    // Assumes:
    //    if x != 0, then x points to an array of size len (which has been allocated)
    // Effects:
    //    if x==0 return -1
    //    else return the index of the n-th even number in array x
    //         or return -1 if there is no n-th even number in array x

    int count = 0;
    if(x == 0){
        return -1;
    }
    for (int i = 0; i < len; i++){
        if ((x[i] & 1) == 0){
            count++;
        }
        if(count = n){
            return i;
        }
    }
    return -1;
}

    /**
     * Says hello to the world.
     * 
     * @param args The arguments of the program.
     */
    public static void main(String[] args) {
        System.out.println("Hello World!");
    }
}
