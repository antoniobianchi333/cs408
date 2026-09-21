import argparse
import grammar
from os.path import exists, abspath
import mmap
import os
import tempfile
import struct
from typing import Any, List, Union
import enum

""" BEGIN UTIL """

def shmem_create(filename: str, size: int) -> str:
    """
    Create a file for accessing shared memory of size

    Parameters
    ---------------
    filename (str): Relative or absolute path to tempfile
    size (int): Number of bytes for the shared memory

    Returns
    ----------------
    created_file_path (str)
    """
    # create a temporary file in /tmp
    temp_file_descriptor, temp_file_path = \
        tempfile.mkstemp(prefix=filename, dir="/tmp")
    
    try:
        os.write(temp_file_descriptor, b'\x00' * size)
        os.fsync(temp_file_descriptor)
    except Exception as e:
        print("[shmem_create]: Exception: ", e.msg)
    finally:
        os.close(temp_file_descriptor)
    
    return temp_file_path

def shmem_open(filename: str) -> Union[None, mmap.mmap]:
    """
    Opens the shared mem and returns

    Parameters
    ----------------
    filename (str): Relative/absolute path to tempfile

    Returns
    ----------------
    None: On error
    mm (mmap.mmap): Array like accessible byte array
    """
    if not exists(filename):
        return None
    

    with open(filename, 'r+b') as file:
        mm = mmap.mmap(file.fileno(), length=0, access=mmap.ACCESS_WRITE)
        return mm

def shemem_close(mm: mmap.mmap):
    """
    Closes a mmap object

    Parameters
    ---------------
    mm (mmap.mmap): mmap object
    """
    mm.close()

def shmem_get_num_edges(mm: mmap.mmap) -> int:
    """
    Obtain the number of edges from shared mem

    Parameters
    -------------
    path (str): Relative path to the shared mem

    Returns
    -------------
    num_edges (str): THe number of edges
    """
    # read the first four bytes as an integer
    val = struct.unpack('I', mm[:4])[0]
    return val

def shmem_get_edge_state(mm: mmap.mmap, edge_num: int) -> bool:
    """
    Check whether an edge was visited

    Parameters
    --------------
    edge_num (int): The edge you wish to check (1-indexed)

    Returns
    --------------
    true: If visited
    false: Otherwise
    """
    if mm[4 + (edge_num - 1)]:
        return True
    return False

def parse_grammer(path: str):
    """
    Parse and return a grammar from parsimonious

    Parameters
    ----------------
    path (str): Relative/absolute path

    Returns
    ----------------
    None: On failure
    Parsimonious object otherwise
    """
    if not exists(abspath(path)):
        return None
    
    return grammar.parse_cfg(abspath(path))

""" END UTIL """

""" BEGIN MUTATOR STUFF"""

class Mutator:
    # TODO: Fix/delete/modify as you wish

    # Contents
    src: str
    
    def __init__(self):
        """
        TODO:
        Constructor
        """

    def update_src(self, input: str):
        """
        Updates the current src content with a new one
        """
        self.src = input

    def mutate(self):
        """
        Mutates the current saved src and returns it.
        This base class should error out
        """
        raise Exception("[Mutator]: Mutate implement in child!")
    
class InsertMutator(Mutator):
    def mutate(self):
        """
        TODO:
        """

class DeleteMutator(Mutator):
    def mutate(self):
        """
        TODO:
        """
class FlipMutator(Mutator):
    def mutate(self):
        """
        TODO:
        """ 
""" END MUTATOR STUFF """

""" BEGIN CORPUS STUFF """

class Corpus:
    # TODO: Should contain some information about
    # mapping a specific seed to the coverage
    def __init__(self):
        """
        TODO:
        Constructor
        """
""" END CORPUS STUFF """

""" BEGIN INPUTGENERATOR STUFF """

class DecisionTree:
    rule_id: int
    children_nonterminals: list['DecisionTree']

class InputGenerator:
    # TODO: Classs to generate input
    
    # Path to grammar file
    grammar_path: str

    def __init__(self, grammar_path: str):
        """
        # TODO:
        Constructor
        """
        self.grammar_path = grammar_path

    def generate(self, nonterminal: Any) -> tuple[str, 'DecisionTree']:
        """
        TODO:
        Expands one non-terminal recursively until no
        more non-terminals exist. It should keep the decision
        tree as it goes so later you can start at any node on the tree
        and continue deriving to mutate this input.

        Parameters
        --------------
        nonterminal (Any): NOTE: You probably want to change type

        Returns
        --------------
        res (str): Expanded terminal
        tree (DecisionTree): decision tree
        """
        return ""

    def mutate(self, tree: DecisionTree) -> str:
        """
        TODO:

        Randomly mutate starting from some node on the decision tree
        it should result in a different resulting seed.
        It should only expand non-terminals. It should also keep track of
        updating the decision tree if you choose to store all data in one
        instance of the decision tree

        Parameters
        --------------
        tree (DecisionTree): decision tree

        Returns
        -----------------
        res (str): Mutated string due to non-terminal triggers
        """
        return ""

""" END INPUT GENERATOR """

""" BEGIN FUZZER STUFF """

class Fuzzer:
    # TODO: Create as many class variables as you need
    # TODO: Add as many functions as you need
    # TODO: Delete this class if you wish

    # Location of output directory
    output_dir: str
    # Path to the instrumented binary to be fuzzed
    harness_path: str
    # Path to the seeds
    seed_dir: str

    # Id of the next bug's folder number
    next_bug_id: int
    # Mutators you can apply
    mutators: List[Mutator]
    # Current corpus
    corpus: Corpus
    # Input Generator
    input_generator: InputGenerator

    # Shared memory
    temp_path: str = ""
    mm: mmap.mmap = None

    def __init__(self, output_dir: str, harness_path: str
                 , seed_dir: str, grammar_path: str
                 ):
        """
        TODO: Set up however you wish
        Constructor
        """
        self.next_bug_id = 0
        # TODO: Make the output directory!
        self.output_dir = abspath(output_dir)
        self.mutators = []
        self.mutators.append(DeleteMutator())
        self.mutators.append(InsertMutator())
        self.mutators.append(FlipMutator())
        self.corpus = Corpus()

        if not exists(abspath(harness_path)):
            print("[Fuzzer]: Harness at " + harness_path + " does not exist!")
            exit(1)

        self.harness_path = abspath(harness_path)

        if not exists(abspath(seed_dir)):
            print("[Fuzzer]: Seed directory at " + seed_dir + " does not exist!")
            exit(1)
        self.seed_dir = seed_dir
        
        if not exists(abspath(grammar_path)):
            print("[Fuzzer]: Grammar at " + grammar_path + " does not exist!")
            exit(1)
        self.input_generator = InputGenerator(abspath(grammar_path))

        # Setup shared memory
        # TODO: CHANGE THE NAME OF THE TEMP FILE!!
        self.temp_path: str = shmem_create("temp", 65536)
        self.mm = shmem_open(self.temp_path)
        assert(self.mm != None)

    def __del__(self):
        """
        TODO: Desctructor
        """
        if self.mm != None:
            shemem_close(self.mm)

    def minimize_input(self, input: str) -> str:
        """
        Parameters
        ---------------
        input (str): Input

        Returns
        ------------
        mimized input
        """
        return input

    def fuzz_one(self):
        """
        TODO:

        Spawns one instance of the harness and obtains
        the results of the harness. Use subprocess.Popen
        to run the harness and set the environment of COV_SHM
        """
        # TODO: Call minimize_input to delete something and rerun harness
        self.minimize_input("")

    def fuzz_loop(self):
        """
        TODO:

        Some loop to continually run the fuzzer with new mutations
        and updating the corpus. It should probably call fuzz_one
        """

""" END FUZZER STUFF """

def parse_args():
    parser = argparse.ArgumentParser(description="Command line argument parser for a fuzzer.")

    parser.add_argument("-o", "--output_dir", required=True, help="Path to the output directory.")
    parser.add_argument("-i", "--seed_dir", help="Path to the seed directory.")
    parser.add_argument("harness", help="The harness file to use.")

    parser.add_argument("-g", "--grammar", help="Path to the grammar file.")
    parser.add_argument("--competition", action="store_true", help="Enable competition mode.")
    parser.add_argument("--greybox", action="store_true", help="Enable greybox fuzzing mode.")

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = parse_args()
    print(f"Output Directory: {args.output_dir}")
    print(f"Seed Directory: {args.seed_dir}")
    print(f"Grammar File: {args.grammar}")
    print(f"Greybox: {'Enabled' if args.greybox else 'Disabled'}")
    print(f"Competition: {'Enabled' if args.competition else 'Disabled'}")
    print(f"Harness: {args.harness}")

    # Runn fuzzer
    f: Fuzzer = Fuzzer(args.output_dir, args.harness, args.seed_dir, args.grammar)
    # f: Fuzzer = Fuzzer( ".", ".", ".", ".")
    f.fuzz_loop()
