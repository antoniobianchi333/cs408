# CS408 Lab1

## Getting Started

1. Create a virtual environment and activate it.
```
$ python3 -m venv .venv
$ source .venv/bin/activate
```

2. Install dependencies.
```
$ pip install -r requirements.txt
```

⚠️ **NOTE:** Make sure you have activated the virtual environment before running your fuzzer. Do NOT install additional packages. All of your fuzzer code should be in fuzzer.py. Do NOT create additional python files.

## Project Structure

Your code must follow the structure listed as follows:

```
.
├── fuzzer.py                   # fuzzer code (task 1, 2, 3, 4) 
├── grammar.py
├── LICENSE
├── project
│   ├── libfyaml
│   │   ├── grammar             # libfyaml grammar (task 4)
│   │   ├── harness.c           # libfyaml harness code (task 2)
│   │   ├── afl_dictionary      # libfyaml afl dictionary (task 5)
│   │   ├── run_afl.sh          # script to run afl (task 5)
│   │   └── seeds               # libfyaml seed directory (task 2, 5)
│   ├── magic
│   │   ├── harness.c           # magic harness code (task 3)
│   │   ├── magic.c             # magic target code (task 3)
│   │   └── seeds               # magic seed directory (task 3)
│   ├── parson                  # similar to libfyaml
│   ├── README.md
│   └── vulnerable
│       ├── harness.c           # harness code (task 1)
│       └── seeds               # vulnerable seed directory (task 1)
├── README.md
└── sancov.c                    # instrumentation runtime (task 2, 3)
```

📝 __NOTE__: You will likely need to change the files annotated with **tasks** to implement the respective project tasks. 