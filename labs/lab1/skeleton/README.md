[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-8d59dc4de5201274e310e4c54b9627a8934c3b88527886e3b421487c677d23eb.svg)](https://classroom.github.com/a/VTRXy3E9)

# Framework structure

The framework consists of the following files and functions.

## Helper Scripts

helper scripts to compile the programs.

### Makefile

The Makefile has several targets you should find useful.

- `library` : this will compile your testlib.so shared object library.
    - Add `coverage=1` to enable the coverage.
- `build_coverage_tests`: this will compile your testlib.so and the *_test.c files in the `coverage_tests/` directory in a way which should be compatible with gcov.
- `run_coverage_tests`: this will run `build_coverage_tests` and then call the `coverage_tests_helper.py` script you must implement.
- `build_dectector_tests`: this will compile your testlib.so and the files in the `dectector_tests/` directory in a way which should be compatible with gcov.
- `run_dectector_tests`: you will need add targets to compile examples and run them with the framework.

### Do Not Modify The Immutable Files

**NOTE**: Please DO NOT modify the files that are listed in `./immutablefiles`.
You will lost the certain points if you modify them.
You can use the following command to check:

```bash
$ bash check_modified.h
```

If you see the output with the file name, such as following, please restore back your changes:
```
Following immutable file(s) are modified and have been added to the git:
MODIFIED: .immutablefiles
MODIFIED: check_modified.sh
MODIFIED: utils.c
MODIFIED: utils.h
MODIFIED: testlib.h
MODIFIED: coverage_tests_sample.py
MODIFIED: LICENSE
MODIFIED: Makefile
MODIFIED: README.md
MODIFIED: coverage_tests/mutex_buggy_test.c
MODIFIED: detector_tests/sample_example.c

Following immutable file(s) are modified:
MODIFIED: .immutablefiles
MODIFIED: check_modified.sh
MODIFIED: README.md
```

## Testing Source Code

- `libunwind/` directory: This contains a compilation of the libunwind library. Don't touch it.
- `utils.h` and `utils.c`: Do not modify these helper functions. They are here to simplify your work. Please use the INFO(...) function defined here instead of printf in your work. This makes it easy to toggle printing when grading.

Following are the file(s) that you need to complete:

- `testlib.h` and `testlib.c`: This is a skeleton for your testing library implementation. The given functions should get intercepted by your library with the help of `LD_PRELOAD`. A simple example has already been added to help you. The last function in testlib.c is a constructor function which will get called at the start of a target programs main function. Don't modify its priority of 200.
- `framework.py`: Wrapper which should greatly simplify setting environment variables when calling a target program with `LD_PRELOAD`. It is strongly recommended to use this in your work. Expand this file to add bug detecting functions to the framework.

## Test Cases

- `coverage_tests_sample.py`: Do not modify this file. Runs all the test files in tests/ with environment variables mathcing what you provide. Finally, it will call gcov.

Following are the file(s) that you need to complete:

- `coverage_tests_helper.py` and `detector_tests_helper.py`: This is where you should implement your testing framework to test your library. The skeleton simply calls `coverage_tests_sample.py`.
- `tests/` directory: This is the directory where you should add programs you can use to test your library implementation.
- `examples/` directory: This is the directory where you should add programs that has a single concurrency bug and that activates a single bug detector.
