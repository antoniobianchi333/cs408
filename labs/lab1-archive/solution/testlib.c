#define _GNU_SOURCE
#include <assert.h> // Use this, it is your friend!
#define UNW_LOCAL_ONLY
#include <libunwind.h>
#include <stdlib.h>

#include "testlib.h"
#include "utils.h"
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <dlfcn.h>
#include <stdatomic.h>
#include <string.h>
#include <valgrind/drd.h>

#define gettid() ((pid_t)syscall(SYS_gettid))

#define MAX_THREAD_CNT 64 // Max number of threads allowed (stated in handout)

/* -------------- QUESTIONS / ISSUES LOG (Q - Question, I - Issue) -----------------------
 * Q - Are we supposed to used INFO() or INFO() for logging? Sometimes it says INFO() in handout.

 * Q - How does one get thread_id of newly made thread from 'parent' thread? Confused on gettid(). 
   A - From Piazza, it seems we should be logging the "THREAD CREATED (<THREAD#>, <THREADID>)" from modified start_routine
       (pre_start_routine) in our case.

 * I - Handout specifies "Will not have more than 64 threads running at one time" however, for indexing problems
       related to storing thread information, we could have more than 64 threads CREATED (not running). I think the
       piazza question asking this somewhat got the answer that we shouldn't CREATE more than 64 threads ever, so should
       be fine?

 * Q - Fat assumption here, the global datastructure containing thread info, each entry should only ever be written to
       by the thread that corresponds to that entry. Meanwhile, other threads may read it over when finding the thread num
       for itself, but other entries aren't pertinent to that thread. Therefore, this DS doesn't need any lock on it at all?
       Not even a read/write lock, because even if an entry is being written to, it can't corrupt another thread. good logic?

 * Q - Where should stacktrack() be called from? Inside print sem block? After fflush? Outside print sem block but before orig_call()?

 * Q - Do we need the calls to scheduler() with param PCT_NO_OP for random scheduler? Piazza post made by quandale, remains to be
       answered.
 */

// Lazy initialize
_Atomic int initialized = 0;

// Global variable saying which scheduling algorithm to use.
int algorithm_id;
// Global variable (boolean) of whether or not to get stacktraces.
int stacktrace_enabled;

// Stack trace called -- prevents infinite loops and local structures being created by stacktrace()
static __thread int in_st = 0;

// Define states for threads (PCT)
enum thread_state {
    P_RUNNABLE,
    P_BLOCKED_MUTEX,
    P_BLOCKED_COND,
    P_UNUSED,
    PCT_THREAD_CREATED,
    PCT_THREAD_EXITED,
    PCT_THREAD_STARTED,
    PCT_MUTEX_LOCKED,
    PCT_MUTEX_UNLOCKED,
    PCT_THREAD_YIELDED,
    PCT_COND_LOCKED,
    PCT_NO_OP
};

// Data structure to interpose start_routine args
typedef struct pre_start_arg {
    void *arg;
    void *(*start_routine)(void *);
} pre_start_arg;

// Data structure to hold thread information
typedef struct thread_data {
    pthread_t thread_id;

    // Store to call free() on when thread exits
    struct pre_start_arg *interposed_arg;

    /* Priority & state information for PCT scheduler */
    int pct_state;

    pthread_mutex_t *mutex_locked_on;
    pthread_cond_t *cond_locked_on;
} thread_data;

// Global array to hold info on each thread
struct thread_data thread_info[MAX_THREAD_CNT];
// Priority
int priority[MAX_THREAD_CNT];
sem_t pct_thread_sems[MAX_THREAD_CNT];

// Global counter to assign thread_num
volatile int thread_count;
// Semaphore used to protect counter
sem_t count_sem;
// Semaphore used to protect printing
sem_t print_sem;
// Semaphore used to protect thread_info access
sem_t thread_sem;

// Mutex
typedef struct mutex_data {
    pthread_mutex_t *mutex;
    pthread_t owner;
} mutex_data;

// Global mutex array
struct mutex_data **mutexes;
volatile int mutexes_count;
volatile int mutexes_size;

// Conditional variable nodes: threads currently waiting on condition variable x
typedef struct cond_node {
    pthread_t thread_id;
    struct cond_node *next;
} cond_node;

// Condition variable head: holds the conditional variable itself, onto which cond_nodes are attached
typedef struct cond_head {
    pthread_cond_t *cond;
    struct mutex_data *m_data;
    struct cond_node *next;
} cond_head;

// Conditional: Array of FIFO queues [linked lists]
struct cond_head **cond_vars;
volatile int cond_vars_count;
volatile int cond_vars_size;

typedef int (*pthread_create_type)();
typedef int (*pthread_exit_type)();
typedef int (*pthread_yield_type)();
typedef int (*pthread_cond_wait_type)();
typedef int (*pthread_cond_signal_type)();
typedef int (*pthread_cond_broadcast_type)();
typedef int (*pthread_mutex_lock_type)();
typedef int (*pthread_mutex_unlock_type)();
typedef int (*pthread_mutex_trylock_type)();

int find_thread_num(int thread_id)
{
    int i;
    int num = -1;
    for (i = 0; i < MAX_THREAD_CNT; i++) {
        if (thread_info[i].thread_id == thread_id) {
            num = i;
            break;
        }
    }

    // Not found
    assert(num != -1);
    return num;
}

/* Shuffle algorithm given by handout to randomize priority array */
void shuffle(int *array, size_t n)
{
    if (n > 1) {
        size_t i;
        for (i = 0; i < n - 1; i++) {
            size_t j = i + rand() / (RAND_MAX / (n - i) + 1);
            int t = array[j];
            array[j] = array[i];
            array[i] = t;
        }
    }
}

int pct_find_highest_ready()
{
    int i;
    int max_prio = -1;
    int thread_num = -1;
    for (i = 0; i < MAX_THREAD_CNT; i++) {
        if (thread_info[i].pct_state == P_RUNNABLE && priority[i] > max_prio) {
            max_prio = priority[i];
            thread_num = i;
        }
    }

    return thread_num;
}

void scheduler(int pct_state)
{
    sem_wait(&thread_sem);
    if (algorithm_id == kAlgorithmPCT) {
        // PCT Algorithm being used
        int curr_thread_num = find_thread_num(gettid());
        switch (pct_state) {
        case PCT_THREAD_CREATED:;
            // This thread is parent of newly created thread,
            // block until new thread reaches pre_start_function
            // which will call scheduler again and then decide which to run
            sem_t *sem_0 = &pct_thread_sems[curr_thread_num];
            sem_post(&thread_sem);
            sem_wait(sem_0);
            break;

        case PCT_MUTEX_UNLOCKED: //Falling through to next one
            thread_info[curr_thread_num].mutex_locked_on = NULL;
        case PCT_THREAD_YIELDED:
        case PCT_THREAD_STARTED:
            if (!(thread_info[curr_thread_num].pct_state == P_BLOCKED_COND)) {
                thread_info[curr_thread_num].pct_state = P_RUNNABLE;
            }
            int thread_to_run_num = pct_find_highest_ready();
            sem_t *sem1 = &pct_thread_sems[thread_to_run_num];
            sem_t *sem2 = &pct_thread_sems[curr_thread_num];
            sem_post(&thread_sem);
            if (thread_to_run_num != curr_thread_num) {
                // thread we want to run is not current, post it and wait this thread
                sem_post(sem1);
                sem_wait(sem2);
            } // Otherwise this is the thread we want to run, just return
            break;

        case PCT_THREAD_EXITED:
            // Set thread to 'dead'
            thread_info[curr_thread_num].pct_state = P_UNUSED;
            int next_thread = pct_find_highest_ready();
            sem_t *sem_1 = &pct_thread_sems[next_thread];
            sem_post(&thread_sem);
            sem_post(sem_1);
            break;

        case PCT_MUTEX_LOCKED:
            // Thread trying lock but lock is already locked
            thread_info[curr_thread_num].pct_state = P_BLOCKED_MUTEX;
            int next_thread1 = pct_find_highest_ready();
            sem_t *sem3 = &pct_thread_sems[next_thread1];
            sem_t *sem4 = &pct_thread_sems[curr_thread_num];
            sem_post(&thread_sem);
            sem_post(sem3);
            sem_wait(sem4);
            break;

        case PCT_COND_LOCKED:
            // Blocking on a conditional
            // The rest is done in PCT_MUTEX_UNLOCKED
            thread_info[curr_thread_num].pct_state = P_BLOCKED_COND;
            sem_post(&thread_sem);
            break;

        default:
            sem_post(&thread_sem);
            break;
        }
        return;
    } else {
        sem_post(&thread_sem);
        // Random Algorithm in use
        if (algorithm_id == kAlgorithmRandom)
            rsleep();
    }
}

void *pre_start_routine(void *interposed_arg)
{
    pthread_detach(pthread_self());
    struct pre_start_arg *params = (struct pre_start_arg *)interposed_arg;

    int thread_id = gettid();
    int thread_num;
    sem_wait(&count_sem);
    thread_num =
        ++thread_count; // Pre increment counter and store value (Main should always have thread num 0)
    sem_post(&count_sem);

    sem_wait(&thread_sem);
    thread_info[thread_num].thread_id = thread_id;
    thread_info[thread_num].pct_state = P_RUNNABLE;
    thread_info[thread_num].interposed_arg = params;
    sem_post(&thread_sem);

    // Log thread creation with relevant info
    sem_wait(&print_sem);
    INFO("THREAD CREATED (%d, %d)\n", thread_num, thread_id);
    sem_post(&print_sem);

    // Call scheduler before executing to see if this is the thread that should be running.
    scheduler(PCT_THREAD_STARTED);

    // Actual call to start_routine:
    void *ret = params->start_routine(params->arg);

    sem_wait(&print_sem);
    INFO("THREAD EXITED (%d, %d)\n", thread_num, thread_id);
    sem_post(&print_sem);

    scheduler(PCT_THREAD_EXITED);

    return ret;
}

// Set the state of the highest priority thread currently blocked by the mutex to runnable
void pct_mutex_set_runnable(pthread_mutex_t *mutex)
{
    int i;
    int tid = -1;
    int prio = -1;
    sem_wait(&thread_sem);
    for (i = 0; i < MAX_THREAD_CNT; i++) {
        if (thread_info[i].mutex_locked_on == mutex && priority[i] > prio &&
            thread_info[i].pct_state == P_BLOCKED_MUTEX) {
            prio = priority[i];
            tid = i;
        }
    }
    sem_post(&thread_sem);

    if (prio > -1) {
        sem_wait(&thread_sem);
        thread_info[tid].pct_state = P_RUNNABLE;
        sem_post(&thread_sem);
    }
}

void stacktrace()
{
    if (!stacktrace_enabled || in_st) {
        return;
    }

    in_st = 1;

    unw_cursor_t cursor;
    unw_context_t context;
    // Initialize cursor to current frame for local unwinding.
    unw_getcontext(&context);
    unw_init_local(&cursor, &context);

    sem_wait(&print_sem);
    INFO("Stacktrace: \n");

    // Unwind frames one by one, going up the frame stack.
    while (unw_step(&cursor) > 0) {
        unw_word_t offset, pc;
        unw_get_reg(&cursor, UNW_REG_IP, &pc);
        if (pc == 0) {
            break;
        }

        char sym[256];
        if (unw_get_proc_name(&cursor, sym, sizeof(sym), &offset) == 0) {
            if (strcmp(&sym, "pre_start_routine") != 0) {
                INFO(" 0x%lx:", pc);
                INFO(" (%s+0x%lx)\n", sym, offset);
            }

        } else {
            INFO(" 0x%lx:", pc);
            INFO(" -- ERROR: unable to obtain symbol name for this frame\n");
        }
    }

    in_st = 0;

    sem_post(&print_sem);
}

void check_and_resize_mutexes()
{
    if (mutexes_count == mutexes_size) {
        sem_wait(&count_sem);
        mutexes_size *= 4;
        mutexes = realloc(mutexes, sizeof(struct mutex_data *) * mutexes_size);
        sem_post(&count_sem);
    }
}

void check_and_resize_cond_vars()
{
    if (cond_vars_count == cond_vars_size) {
        sem_wait(&count_sem);
        cond_vars_size *= 4;
        cond_vars =
            realloc(cond_vars, sizeof(struct cond_head *) * cond_vars_size);
        fflush(stdout);
        sem_post(&count_sem);
    }
}

void initialize(void)
{
    if (initialized) {
        return;
    }
    // Initialize semaphore for LOG prints
    sem_init(&print_sem, 0, 1);
    // Initialize semaphore for global thread counter
    sem_init(&count_sem, 0, 1);

    sem_wait(&print_sem);
    initialized = 1;
    thread_count = 0;

    INFO("Testlib loaded!\n");
    INFO("Stacktraces is %i\n", stacktrace_enabled);
    INFO("Algorithm ID is %i\n", algorithm_id);
    INFO("Seed is %i\n", (int)get_seed());

    sem_post(&print_sem);

    // Initialize semaphore for thread_info
    sem_init(&thread_sem, 0, 1);

    // Initialize global thread array and priority array
    sem_wait(&thread_sem);

    thread_info[0].thread_id = gettid();
    priority[0] = 0;
    thread_info[0].mutex_locked_on = NULL;
    thread_info[0].cond_locked_on = NULL;
    sem_init(&pct_thread_sems[0], 0, 0);

    int i;
    for (i = 1; i < MAX_THREAD_CNT; i++) {
        thread_info[i].thread_id = -1;

        // Add more stuff as needed
        // PCT stuff
        priority[i] = i;
        thread_info[i].pct_state = P_UNUSED;
        thread_info[i].mutex_locked_on = NULL;
        thread_info[i].cond_locked_on = NULL;

        sem_init(&pct_thread_sems[i], 0, 0);
    }

    shuffle(priority, MAX_THREAD_CNT);

    sem_post(&thread_sem);
}

/*----------------------------- End Custom Functions ----------------------------------*/

// Thread Management
int pthread_create(pthread_t *thread, const pthread_attr_t *attr,
                   void *(*start_routine)(void *), void *arg)
{
    initialize();

    pthread_create_type orig_create;
    orig_create = (pthread_create_type)dlsym(RTLD_NEXT, "pthread_create");

    struct pre_start_arg *interposed_arg = malloc(sizeof(struct pre_start_arg));
    interposed_arg->arg = arg;
    interposed_arg->start_routine = start_routine;

    void *(*temp) = start_routine;

    // Log call
    sem_wait(&print_sem);
    INFO("CALL pthread_create(%p, %p, %p, %p)\n", thread, attr, start_routine,
         arg);
    sem_post(&print_sem);

    stacktrace();

    // TODO: double check examples after uncommenting this
    scheduler(PCT_NO_OP);

    int ret_val =
        orig_create(thread, attr, &pre_start_routine, (void *)interposed_arg);

    sem_wait(&print_sem);
    INFO("RETURN pthread_create(%p, %p, %p, %p) = %x\n", thread, attr, temp,
         arg, ret_val);
    sem_post(&print_sem);

    scheduler(PCT_THREAD_CREATED);

    return ret_val;
}

void pthread_exit(void *retval)
{
    initialize();

    // TODO: Implement
    int thread_id = gettid();
    int thread_num = find_thread_num(thread_id);

    pthread_exit_type orig_exit;
    orig_exit = (pthread_exit_type)dlsym(RTLD_NEXT, "pthread_exit");

    sem_wait(&print_sem);
    INFO("CALL pthread_exit(%p)\n", retval);
    sem_post(&print_sem);

    stacktrace();

    scheduler(PCT_NO_OP);

    sem_wait(&print_sem);
    INFO("THREAD EXITED (%d, %d)\n", thread_num, thread_id);
    sem_post(&print_sem);

    scheduler(PCT_THREAD_EXITED);

    orig_exit(retval);
}

int pthread_yield(void)
{
    initialize();

    pthread_yield_type orig_yield;
    orig_yield = (pthread_yield_type)dlsym(RTLD_NEXT, "pthread_yield");

    sem_wait(&print_sem);
    INFO("CALL pthread_yield()\n");
    sem_post(&print_sem);

    stacktrace();

    scheduler(PCT_NO_OP);

    int ret_val = orig_yield();

    sem_wait(&print_sem);
    INFO("RETURN pthread_yield() = %x\n", ret_val);
    sem_post(&print_sem);

    scheduler(PCT_THREAD_YIELDED);

    return ret_val;
}

// Condition variables
int pthread_cond_wait(pthread_cond_t *cond, pthread_mutex_t *mutex)
{
    initialize();

    sem_wait(&print_sem);
    INFO("CALL pthread_cond_wait(%p, %p)\n", cond, mutex);
    sem_post(&print_sem);

    stacktrace();

    int ret_val = 1;

    if (algorithm_id == kAlgorithmRandom || algorithm_id == kAlgorithmNone) {
        scheduler(PCT_NO_OP);
        pthread_cond_wait_type orig_cond_wait;
        orig_cond_wait =
            (pthread_cond_wait_type)dlsym(RTLD_NEXT, "pthread_cond_wait");
        ret_val = orig_cond_wait(cond, mutex);
    } else { // PCT
        struct mutex_data *mut_data = NULL;
        int i;
        // Check curr thread owns the mutex and that mutex has been registered via mutex_lock
        for (i = 0; i < mutexes_count; i++) {
            assert(mutexes[i] != NULL);
            if (mutexes[i]->mutex == mutex && mutexes[i]->owner == gettid()) {
                mut_data = mutexes[i];
                break;
            }
        }

        if (mut_data == NULL) {
            scheduler(PCT_NO_OP);

            sem_wait(&print_sem);
            INFO("RETURN pthread_cond_wait(%p, %p) = %x\n", cond, mutex,
                 ret_val);
            sem_post(&print_sem);

            scheduler(PCT_NO_OP);

            return ret_val;
        }

        // INFO("WE GOT TO THE LOOP - and cond_vars_count is: %d\n", cond_vars_count);
        // Custom implemention
        struct cond_head *c_head = NULL;
        for (i = 0; i < cond_vars_count; i++) {
            // INFO("WE GOT INSIDE THE LOOP\n");
            if (cond_vars[i]->cond == cond) {
                // INFO("cond_vars[i]->cond == cond -- TRUE\n");
                if (cond_vars[i]->next ==
                    NULL) { // Non-concurrent call to pre-existing conditional currently not in use. Can simply reuse the struct with reassigned mutex.
                    cond_vars[i]->m_data = mut_data;
                } else if (
                    !(cond_vars[i]->m_data ==
                      mut_data)) { // Can't have 1 cond var going on different mutexes at the same time

                    scheduler(PCT_NO_OP);

                    sem_wait(&print_sem);
                    INFO("RETURN pthread_cond_wait(%p, %p) = %x\n", cond, mutex,
                         ret_val);
                    sem_post(&print_sem);

                    scheduler(PCT_NO_OP);

                    return ret_val;
                }
                c_head = cond_vars[i];
                break;
            }
        }

        if (!c_head) { // Create a new conditional variable
            int c_count;
            sem_wait(&count_sem);
            c_count = cond_vars_count++;
            sem_post(&count_sem);

            cond_vars[c_count] = malloc(sizeof(struct cond_head));
            cond_vars[c_count]->cond = cond;
            cond_vars[c_count]->m_data = mut_data;

            c_head = cond_vars[c_count];

            check_and_resize_cond_vars();
        }

        struct cond_node *c_node = malloc(sizeof(struct cond_node));
        c_node->thread_id = gettid();
        c_node->next = NULL;

        // Put into queue
        if (c_head->next == NULL) {
            c_head->next = c_node;
        } else {
            struct cond_node *c_node_head = c_head->next;
            while (c_node_head->next != NULL) {
                c_node_head = c_node_head->next;
            }
            c_node_head->next = c_node;
        }

        int t_num = find_thread_num(gettid());

        sem_wait(&thread_sem);
        thread_info[t_num].cond_locked_on = cond;
        sem_post(&thread_sem);

        scheduler(PCT_COND_LOCKED);

        // pthread_cond_wait unlocks the mutex and blocks here
        pthread_mutex_unlock(mutex);

        // pthread_cond_wait reacquires mutex when unblocked
        pthread_mutex_lock(mutex);

        ret_val = 0;
    } // end PCT algo

    sem_wait(&print_sem);
    INFO("RETURN pthread_cond_wait(%p, %p) = %x\n", cond, mutex, ret_val);
    sem_post(&print_sem);

    scheduler(PCT_NO_OP);

    return ret_val;
}

int pthread_cond_signal(pthread_cond_t *cond)
{
    initialize();

    sem_wait(&print_sem);
    INFO("CALL pthread_cond_signal(%p)\n", cond);
    sem_post(&print_sem);

    stacktrace();

    scheduler(PCT_NO_OP);

    int ret_val = 1;

    if (algorithm_id == kAlgorithmRandom || algorithm_id == kAlgorithmNone) {
        pthread_cond_signal_type orig_cond_signal;
        orig_cond_signal =
            (pthread_cond_signal_type)dlsym(RTLD_NEXT, "pthread_cond_signal");
        ret_val = orig_cond_signal(cond);
    } else { // PCT
        // Custom implemention
        int i;
        struct cond_node *c_node;
        for (i = 0; i < cond_vars_count; i++) {
            if (cond_vars[i]->cond == cond) {
                // Get and remove top of queue for cond var x
                c_node = cond_vars[i]->next;
                cond_vars[i]->next = c_node->next;

                // Unblock thread from cond var: is now locked on the respective mutex
                int t_num = find_thread_num(c_node->thread_id);

                sem_wait(&thread_sem);
                thread_info[t_num].cond_locked_on = NULL;
                thread_info[t_num].pct_state = P_RUNNABLE;
                sem_post(&pct_thread_sems[t_num]);
                sem_post(&thread_sem);

                break;
            }
        }

        if (c_node) {
            ret_val = 0;
        }
    } // end PCT

    sem_wait(&print_sem);
    INFO("RETURN pthread_cond_signal(%p) = %x\n", cond, ret_val);
    sem_post(&print_sem);

    scheduler(PCT_NO_OP);

    return ret_val;
}

int pthread_cond_broadcast(pthread_cond_t *cond)
{
    initialize();

    sem_wait(&print_sem);
    INFO("CALL pthread_cond_broadcast(%p)\n", cond);
    sem_post(&print_sem);

    stacktrace();

    scheduler(PCT_NO_OP);

    int ret_val = 1;

    if (algorithm_id == kAlgorithmRandom || algorithm_id == kAlgorithmNone) {
        pthread_cond_broadcast_type orig_cond_broadcast;
        orig_cond_broadcast = (pthread_cond_broadcast_type)dlsym(
            RTLD_NEXT, "pthread_cond_broadcast");
        ret_val = orig_cond_broadcast(cond);
    } else { // PCT
        // Custom implementation
        int i;
        for (i = 0; i < cond_vars_count; i++) {
            if (cond_vars[i]->cond == cond) {
                // Get top of queue
                struct cond_node *c_node = cond_vars[i]->next;
                cond_vars[i]->next = NULL;

                // Clear out entire queue
                while (c_node != NULL) {
                    // Unblock thread from cond var: is now locked on the respective mutex
                    int t_num = find_thread_num(c_node->thread_id);
                    sem_wait(&thread_sem);
                    thread_info[t_num].cond_locked_on = NULL;
                    sem_post(&pct_thread_sems[t_num]);
                    sem_post(&thread_sem);

                    c_node = c_node->next;
                }

                ret_val = 0;
                break;
            }
        }
    }

    sem_wait(&print_sem);
    INFO("RETURN pthread_cond_broadcast(%p) = %x\n", cond, ret_val);
    sem_post(&print_sem);

    scheduler(PCT_NO_OP);

    return ret_val;
}

// Mutexes
int pthread_mutex_lock(pthread_mutex_t *mutex)
{
    initialize();

    pthread_mutex_lock_type orig_mutex_lock;
    orig_mutex_lock =
        (pthread_mutex_lock_type)dlsym(RTLD_NEXT, "pthread_mutex_lock");
    if (in_st) {
        return orig_mutex_lock(mutex);
    }

    sem_wait(&print_sem);
    INFO("CALL pthread_mutex_lock(%p)\n", mutex);
    sem_post(&print_sem);

    stacktrace();

    scheduler(PCT_NO_OP);

    int ret_val = 1;
    if (algorithm_id == kAlgorithmRandom || algorithm_id == kAlgorithmNone) {
        ret_val = orig_mutex_lock(mutex);
    } else {
        pthread_mutex_trylock_type orig_mutex_trylock;
        orig_mutex_trylock = (pthread_mutex_trylock_type)dlsym(
            RTLD_NEXT, "pthread_mutex_trylock");
        ret_val = orig_mutex_trylock(mutex);
        if (ret_val !=
            0) { // Lock is already taken (and thus already exists as well)
            sem_wait(&print_sem);
            INFO("RETURN pthread_mutex_lock(%p) = %x\n", mutex, ret_val);
            sem_post(&print_sem);

            sem_wait(&thread_sem);
            thread_info[find_thread_num(gettid())].mutex_locked_on = mutex;
            sem_post(&thread_sem);

            scheduler(PCT_MUTEX_LOCKED);

            return ret_val;
        }

        int exists = 0;
        int i;
        for (i = 0; i < mutexes_count; i++) {
            if (mutexes[i]->mutex == mutex) {
                mutexes[i]->owner = gettid();
                exists = 1;
                break;
            }
        }

        if (!exists) {
            int m_count;
            sem_wait(&count_sem);
            m_count = mutexes_count++;
            sem_post(&count_sem);

            mutexes[m_count] = malloc(sizeof(struct mutex_data));
            mutexes[m_count]->mutex = mutex;
            mutexes[m_count]->owner = gettid();
            check_and_resize_mutexes();
        }

        ret_val = 0;
    } // end PCT

    sem_wait(&print_sem);
    INFO("RETURN pthread_mutex_lock(%p) = %x\n", mutex, ret_val);
    sem_post(&print_sem);

    scheduler(PCT_NO_OP);

    return ret_val;
}

int pthread_mutex_unlock(pthread_mutex_t *mutex)
{
    initialize();

    pthread_mutex_unlock_type orig_mutex_unlock;
    orig_mutex_unlock =
        (pthread_mutex_unlock_type)dlsym(RTLD_NEXT, "pthread_mutex_unlock");

    if (in_st) {
        return orig_mutex_unlock(mutex);
    }

    sem_wait(&print_sem);
    INFO("CALL pthread_mutex_unlock(%p)\n", mutex);
    sem_post(&print_sem);

    stacktrace();

    scheduler(PCT_NO_OP);

    int ret_val = 1;
    if (algorithm_id == kAlgorithmRandom || algorithm_id == kAlgorithmNone) {
        ret_val = orig_mutex_unlock(mutex);
    } else {
        pct_mutex_set_runnable(mutex);

        int i;
        for (i = 0; i < mutexes_count; i++) {
            if (mutexes[i]->mutex == mutex) {
                mutexes[i]->owner = NULL;
                break;
            }
        }

        ret_val = orig_mutex_unlock(mutex);
    }

    sem_wait(&print_sem);
    INFO("RETURN pthread_mutex_unlock(%p) = %x\n", mutex, ret_val);
    sem_post(&print_sem);

    scheduler(PCT_MUTEX_UNLOCKED);

    return ret_val;
}

int pthread_mutex_trylock(pthread_mutex_t *mutex)
{
    initialize();

    pthread_mutex_trylock_type orig_mutex_trylock;
    orig_mutex_trylock =
        (pthread_mutex_trylock_type)dlsym(RTLD_NEXT, "pthread_mutex_trylock");

    sem_wait(&print_sem);
    INFO("CALL pthread_mutex_trylock(%p)\n", mutex);
    sem_post(&print_sem);

    stacktrace();

    scheduler(PCT_NO_OP);

    int ret_val = orig_mutex_trylock(mutex);

    sem_wait(&print_sem);
    INFO("RETURN pthread_mutex_trylock(%p) = %x\n", mutex, ret_val);
    sem_post(&print_sem);

    scheduler(PCT_NO_OP);

    return ret_val;
}

// This will get called at the start of the target programs main function
static __attribute__((constructor)) void init_testlib(void)
{
    // You can initialize stuff here
    algorithm_id = get_algorithm_ID();
    stacktrace_enabled = get_stacktraces();

    // Initialize array of FIFO queues for conditionals. Start with 16, probably won't get larger than that.
    cond_vars_size = 1;
    cond_vars = malloc(sizeof(struct cond_head *) * cond_vars_size);
    cond_vars_count = 0;

    // Initialize global mutex array. Start with 16, probably won't get larger than that.
    mutexes_size = 1;
    mutexes = malloc(sizeof(struct mutex_data *) * mutexes_size);
    mutexes_count = 0;

    // Set main thread as runnable and start
    thread_info[0].pct_state = P_RUNNABLE;
}

// This will get called at the end of the target's main function
static __attribute__((destructor)) void destroy_testlib(void)
{
    // Interposed args
    int i;
    for (i = 1; i < thread_count; i++) {
        free(thread_info[i].interposed_arg);
    }

    // Array of structs
    for (i = 0; i < mutexes_count; i++) {
        free(mutexes[i]);
    }
    free(mutexes);

    // Array of linked lists
    struct cond_head *head;
    for (i = 0; i < cond_vars_count; i++) {
        head = cond_vars[i];
        struct cond_node *node = head->next;
        struct cond_node *tmp_node;
        while (node != NULL) {
            tmp_node = node;
            node = node->next;
            free(tmp_node);
        }
        free(head);
    }
    free(cond_vars);
}
