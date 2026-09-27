import os
import json

def collect_edges(output_dir: str) -> list[int]:
        # for each output_dir/corpus/[dir]/new_edges, read each line to get the edge id
        # return a list of all edge ids
        edges = set()
        corpus_dir = f"{output_dir}/corpus"
        for dir in os.listdir(corpus_dir):
                new_edges_file = f"{corpus_dir}/{dir}/new_edges"
                if os.path.exists(new_edges_file):
                        with open(new_edges_file, "r") as f:
                                for line in f:
                                        edges.add(int(line.strip()))
        return list(edges)

def collect_corpus_input(output_dir: str) -> list[str]:
        # for each output_dir/corpus/[dir]/input, read the file to get the input
        # return a list of all inputs
        inputs = []
        corpus_dir = f"{output_dir}/corpus"
        for dir in os.listdir(corpus_dir):
                input_file = f"{corpus_dir}/{dir}/input"
                if os.path.exists(input_file):
                        with open(input_file, "r") as f:
                                inputs.append(f.read().strip())
        return inputs

class Bug:
        def __init__(self, type: str, input: str, output: str):
                self.type = type
                self.input = input
                self.output = output
        def to_dict(self):
                return {
                        'type': self.type,
                        'input': self.input,
                        'output': self.output,
                }
        def to_json(self):
                return json.dumps(self.to_dict(), indent=4)
        def __str__(self):
                return self.to_json()
        def __repr__(self) -> str:
                return str(self)

def collect_bugs(output_dir: str) -> list[Bug]:
        # for each output_dir/bugs/[dir], read the type, out, and input files
        # return a list of Bug objects
        bugs = []
        bugs_dir = f"{output_dir}/bugs"
        for dir in os.listdir(bugs_dir):
                type_file = f"{bugs_dir}/{dir}/type"
                input_file = f"{bugs_dir}/{dir}/input"
                output_file = f"{bugs_dir}/{dir}/out"
                if os.path.exists(type_file) and os.path.exists(input_file) and os.path.exists(output_file):
                        with open(type_file, "r") as f:
                                type = f.read().strip()
                        with open(input_file, "r") as f:
                                input = f.read().strip()
                        with open(output_file, "r") as f:
                                output = f.read().strip()
                        bugs.append(Bug(type, input, output))
        return bugs

class FuzzerResult:
        def __init__(self, output_dir: str, output: str, ret_code: int):
                self.ret_code = ret_code
                self.output_dir = output_dir
                self.err_str = ""
                self.edges = None
                try:
                        self.edges = collect_edges(output_dir)
                except Exception as e:
                        self.err_str += str(e)
                self.bugs = None
                try:
                        self.bugs = collect_bugs(output_dir)
                except Exception as e:
                        self.err_str += '\n' + str(e)
                self.corpus = None
                try:
                        self.corpus = collect_corpus_input(output_dir)
                except Exception as e:
                        self.err_str += '\n' + str(e)
                self.output = output
        def to_dict(self):
                return {
                        'ret_code': self.ret_code,
                        # at most 300 characters of the output if it is too long
                        'output': self.output[:300] + "..." if len(self.output) > 300 else self.output,
                        'edges': self.edges,
                        'bugs': [] if self.bugs is None else [bug.to_dict() for bug in self.bugs],
                        'errors': self.err_str,
                        'corpus': self.corpus
                }
        def to_json(self):
                return json.dumps(self.to_dict(), indent=4)
        def __str__(self):
                return self.to_json()
        def __repr__(self) -> str:
                return str(self)

if __name__ == "__main__":
        import sys
        if len(sys.argv) != 2:
                print(f"Usage: {sys.argv[0]} <output_dir>")
                sys.exit(1)
        output_dir = sys.argv[1]
        # for each dir in output dir, call FuzzerResult
        # print the results
        results = {}
        for dir in os.listdir(output_dir):
                output_file = f"{output_dir}/{dir}/output"
                ret_code_file = f"{output_dir}/{dir}/ret_code"
                if os.path.exists(output_file) and os.path.exists(ret_code_file):
                        with open(output_file, "r") as f:
                                output = f.read()
                        with open(ret_code_file, "r") as f:
                                ret_code = int(f.read())
                        results[dir] = FuzzerResult(f"{output_dir}/{dir}/out", output, ret_code)
        # sort the results by the group ID 
        results = {k: results[k] for k in sorted(results.keys())}
        print(json.dumps({k: results[k].to_dict() for k in results.keys()}, indent=4))