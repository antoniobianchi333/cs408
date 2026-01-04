#include <unistd.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <fcntl.h>
#include <stdio.h>

/* BOTH PROCESSES USE HE AME IMPORTS */

/* WRITER PROCESS */
int main() {
    // Open file to write to
    int fdout = open("/tmp/testwrite", 
      O_RDWR | O_CREAT | O_TRUNC, 00666);
    // Can't be a 0 byte sized file
    write(fdout, "", 1);
    // Make this accessible as a buffer
    char * m = mmap (0, 26, 
      PROT_READ | PROT_WRITE, MAP_SHARED, fdout, 0);
    // Infinite loop write a-z
    while(1) {
      for(int i = 0 ; i < 26 ; i++) {
        m[i] = 'a' + i;
      }
    }
    close(fdout);
}

/* READER PROCESS */
int main() {
    int fdin = open("/tmp/testwrite", O_RDWR, 00666);
    char * m = mmap (0, 26, PROT_READ, MAP_SHARED, fdin, 0);
    // infinitely prints a-z
    while(1) {
      for(int i = 0 ; i < 26 ; i++) {
        printf("%d %c\n", i, m[i]);
      }
    }
    close(fdin);
}