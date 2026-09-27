## Postmortem

Handout:
1. Clearly list commands that we will use in testing; plus rubrics/warninsg of not inpelementing CLI.

Skeleton code:
1. Provide test scripts. It should test the fuzzer in the same way as ours.
2. Provide tarball scripts, which also check if certain files exist, remove unnecessary files (e.g., `__pycache__`, static libraries, etc.)
3. Provide lcov to let them reason about code coverage.

## New ideas
1. Some ideas are from https://github.com/antonio-morales/Fuzzing101.
2. Dictionary-based mutator.
3. Let their fuzzer reproduces a real-world bug (e.g., Heartbleed). This should make this lab more fun.
4. Concolic execution.
5. Inject bugs and grade their fuzzers based on how many bugs they can find (just like lab1).