/*
 * DO NOT MODIFY THIS FILE
 */

#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "utils.h"

int *priorities;

int string_equal(const char *str1, const char *str2)
{
    return strcmp(str1, str2) == 0;
}

// We generate a seed based on the SEED environment variable
uint64_t get_seed()
{
    char *seed_var = getenv("SEED");
    return strtoull(seed_var, NULL, 10);
}

int get_algorithm_ID()
{
    char *algorithm_var = getenv("ALGORITHM");
    if (string_equal(algorithm_var, "random"))
        return kAlgorithmRandom;
    assert(string_equal(algorithm_var, "none"));
    return kAlgorithmNone;
}

int get_stacktraces()
{
    char *stacktraces_var = getenv("STACKTRACES");
    return string_equal(stacktraces_var, "True");
}

void make_unique(int *array, size_t idx)
{
    int unique = 0;
    while (!unique) {
        unique = 1;
        for (size_t j = 0; j < idx; ++j) {
            if (array[idx] == array[j]) {
                unique = 0;
                array[idx]++;
                break;
            }
        }
    }
}

void initialize_priorities(int *array, size_t size)
{
    int max_val = 100000;
    srand(get_seed());
    for (size_t i = 0; i < size; ++i) {
        array[i] = rand() % max_val;
        make_unique(array, i);
    }
}

int *get_priorities()
{
    return priorities;
}

int seed_set = 0;

// FIXME: 1000 is to simple, change to 1024 or other more complicated.
#define MAGIC_NUMBER 1000

void rsleep()
{
    rsleep_with_arg(MAGIC_NUMBER);
}

// Helper function.
void rsleep_with_arg(int mod)
{
    assert(mod >= 1);
    assert(seed_set);
    usleep((rand() % mod) * MAGIC_NUMBER);
}

// This will get called before any other code.
static __attribute__((constructor(150))) void init_utils(void)
{
    priorities = (int *)malloc(64 * sizeof(int));
    initialize_priorities(priorities, 64);
    int seed = get_seed();
    srand(seed);
    seed_set = 1;

#ifdef GRADING
    printf("0:%i", priorities[0]);
    for (int i = 1; i < 64; ++i) {
        printf(", %i:%i", i, priorities[i]);
    }
    printf("\n");
#endif
}
