# ----------------------------------------------------------------------#
# In this file you need to add code to run your unit testing framework. #
# You can refer to coverage_tests_sample.py for ideas on how you could  #
# do this. This program gets called by the Makefile when running        #
# "make run_detector_tests".                                            #
# ----------------------------------------------------------------------#

import argparse
import os
import subprocess

# Source: https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
def str2bool(v):
  if isinstance(v, bool):
    return v
  if v.lower() in ('yes', 'true', 't', 'y', '1'):
    return "True"
  elif v.lower() in ('no', 'false', 'f', 'n', '0'):
    return "False"
  else:
    raise argparse.ArgumentTypeError('Boolean value expected.')

parser = argparse.ArgumentParser(description="Concurrent program testing")
parser.add_argument('-s', choices=["none", "pct", "random"], default="none", action="store", dest="algorithm")
parser.add_argument('-n', type=int, default=1, action="store", dest="iterations")
parser.add_argument('-st', type=str2bool, default=False, action="store", dest="stacktraces")
parser.add_argument('-seed', type=int, default=0, action="store", dest="seed")
parser.add_argument('-detector', type=str, required=True, dest='detector')
args = parser.parse_args()

if args.detector and not set(args.detector.split(',')).issubset(["crash", "perf", "dr", "memory"]):
  raise argparse.ArgumentError('Invalid detector')

directory = "detector_tests/"
for filename in os.listdir(directory):
  if filename.endswith(".c"):
    continue

  full_filename = directory + filename
  
  if args.detector:
    command = "python3 framework.py -s={} -n={} -st={} -seed={} -detector={} {}".format(args.algorithm, args.iterations, args.stacktraces, args.seed, args.detector, full_filename)

    print(command)
    print(command.split(" "))
    rc = subprocess.run(command.split(" "))
