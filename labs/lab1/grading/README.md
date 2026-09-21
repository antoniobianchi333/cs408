**Prerequisite:** docker.

**To run tests:**
1. Copy student's submission to the `submissions` directory.
2. Run `make`, which will build a docker image `cs408-lab1`.
3. Run `./test.sh <test_name>` to run tests, e.g., `./test.sh blackbox_basic`, then check the results in `data/`