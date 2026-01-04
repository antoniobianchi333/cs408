#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>

struct cov_map
{
        uint32_t n_edges;
        uint8_t cov[];
};

const int COV_MAP_SIZE = 65536;

struct cov_map *mmap_cov_map()
{
        char *filePath = getenv("COV_SHM");
        if (filePath == NULL)
        {
                fprintf(stderr, "COV_SHM is not set\n");
                return NULL;
        }
        const size_t size = COV_MAP_SIZE;

        int fd = open(filePath, O_RDWR);
        if (fd == -1)
        {
                fprintf(stderr, "cannot open COV_SHM file %s\n", filePath);
                return NULL;
        }

        // map is the starting address of shared memory
        void *map = mmap(NULL, size, PROT_READ | PROT_WRITE,
                         MAP_SHARED, fd, 0);
        if (map == MAP_FAILED)
        {
                close(fd);
                fprintf(stderr, "cannot mmap\n");
                return NULL;
        }

        close(fd);
        return (struct cov_map *)map;
}

struct cov_map *__cov_m;
uint32_t __edges_cnt;

// Note: This functions is called automatically by the compiler instrumentation
// when the hareness starts
void __sanitizer_cov_trace_pc_guard_init(uint32_t *start, uint32_t *stop)
{
        // initialize cov map
        if (__cov_m == NULL)
        {
                __cov_m = mmap_cov_map();
                if (__cov_m == NULL)
                {
                        exit(1);
                }
        }

        // assign edge IDs (ID starting from 1) by updating [start, stop)
        for (uint32_t *g = start; g < stop; g++)
        {
                // TODO: increase __edges_cnt

                // TODO: write __edges_cnt to *g
        }

        // TODO: write __edges_cnt to coverage map n_edges

        return;
}

// Note: This functions is called automatically by the compiler instrumentation
// when an edge of the harness process is visited
void __sanitizer_cov_trace_pc_guard(uint32_t *guard)
{
        // TODO:
        // read *guard to get the edge ID, then update the cov[ID-1] byte to 1

        return;
}

// Note: This functions is called automatically by the compiler instrumentation
// when a constant comparison of 1-byte operands occurs
void __sanitizer_cov_trace_const_cmp1(uint8_t arg1, uint8_t arg2)
{
        // TODO:
        // update the cmplog map

        return;
}

// Note: This functions is called automatically by the compiler instrumentation
// when a constant comparison of 2-byte operands occurs
void __sanitizer_cov_trace_const_cmp2(uint16_t arg1, uint16_t arg2)
{
        // TODO:
        // update the cmplog map

        return;
}

// Note: This functions is called automatically by the compiler instrumentation
// when a constant comparison of 4-byte operands occurs
void __sanitizer_cov_trace_const_cmp4(uint32_t arg1, uint32_t arg2)
{
        // TODO:
        // update the cmplog map

        return;
}

// Note: This functions is called automatically by the compiler instrumentation
// when a constant comparison of 8-byte operands occurs
void __sanitizer_cov_trace_const_cmp8(uint64_t arg1, uint64_t arg2)
{
        // TODO:
        // update the cmplog map

        return;
}