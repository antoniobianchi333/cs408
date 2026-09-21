## Setup

Decompress the fuzzing target source, e.g.,

```sh
cd parson
tar -xvzf parson.tar.gz
```

## Build Libfyaml and Parson Harness

You can use the Makefile we provided to build the different types of harness for Libfyaml and Parson.

```sh
make            # build the blackbox fuzzer harness 
make instrument # build the greybox fuzzer harness
make afl        # build the afl harness
make clean      # cleanup
```
