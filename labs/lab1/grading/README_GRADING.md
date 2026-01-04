# Instructions

See `grading.py`.
You need to manually download the student groups and the root dir:

```bash
# files

Makefile        # Sometime, students will modify the files, we overwrite back
libunwind
ta_test_cases


# grading script

overwrite.py
grading.py
grading_A.py # same as grading.py except the students dir
grading_B.py # same as grading.py except the students dir

# students source code

students
students_A # subset of students
students_B # subset of students

# Regrad request dir

regarded_students
regarding_students


# Moss

build_moss_cmd.py   # Generate the list of testlib.c and framework.py
moss                # e.g., moss -l python  students_A/group_17/framework.py student_A/group_1x/...
```

---

# OLD Instructions

Grading instructions:

The grading involves the following steps:

1) Call make clean. This is necessary as the students tend to upload binaries and object files, so the calls to make will not overwrite these and we may not have permissions.
2) Call make test > grading_make_test.out
	It may take several minutes, please wait
3) Check gcov output and coverage pdf to give points
	output has a line "lines executed XXX" to show the coverage
4) cp TestPrograms/ directory into project directory
	run 'make all' to compile them
5) run the None test programs with the help of framework.py and check the output for points
	e.g. python3 framework.py -s none -n 1 -st=true -seed=10 TestPrograms/argument_test
6) Add the -DNO_LOGING flag to the makefile
7) Recompile the library
8) Run the Random programs with the help of framework.py and check interleavings to give points
	e.g. python3 framework.py -s random -n 5 -st=false -seed=10 TestPrograms/random_test
9) Run the PCT programs with the help of framework.py and check the interleavings for points as well as wether the deadlocks are found
	e.g. python3 framework.py -s pct -n 5 -st=false -seed=10 TestPrograms/deadlock_1_test
10) Run the crash/memory/dr/performance to in the TestPrograms to check students' bug detectors 
	e.g. python3 framework.py -s pct -n 5 -st=false -seed=10 -detector=dr,crash,memory,perf TestPrograms/crash
	python3 framework.py -s pct -n 100 -st=false -seed=1 -detector=perf TestPrograms/perf
	Noted that the perf.c I provide may be detected with memory error
11) Make students' test programs under tests/ examples/ to see if it can be compiled

