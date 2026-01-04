#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>

struct cov_map {
  uint32_t n_edges;
  uint8_t cov[];
};

const int COV_MAP_SIZE = 65536;

struct cov_map *mmap_cov_map() {
  char *filePath = getenv("COV_SHM");
  if (filePath == NULL) {
    fprintf(stderr, "COV_SHM is not set\n");
    return NULL;
  }
  const size_t size = COV_MAP_SIZE;

  int fd = open(filePath, O_RDWR);
  if (fd == -1) {
    fprintf(stderr, "cannot open COV_SHM file %s\n", filePath);
    return NULL;
  }

  // map is the starting address of shared memory
  void *map = mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
  if (map == MAP_FAILED) {
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
void __sanitizer_cov_trace_pc_guard_init(uint32_t *start, uint32_t *stop) {
  // initialize cov map
  if (__cov_m == NULL) {
    __cov_m = mmap_cov_map();
    if (__cov_m == NULL) {
      exit(1);
    }
  }

  // assign edge IDs (ID starting from 1) by updating [start, stop)
  __edges_cnt = 0;
  for (uint32_t *g = start; g < stop; g++) {
    ++__edges_cnt;
    uint32_t edge_id = __edges_cnt;
    *g = edge_id;
    __cov_m->cov[edge_id] = 0;
  }

  __cov_m->n_edges = __edges_cnt;

  return;
}

void __sanitizer_cov_trace_pc_guard(uint32_t *guard) {
  uint32_t id = *guard;
  __cov_m->cov[id-1] = 1;
  return;
}
