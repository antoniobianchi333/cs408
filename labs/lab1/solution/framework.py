# ----------------------------------------------------------------------#
# You do not have to modify this file while working on section 3.       #
# Expand the file to support bug detecting functions on section 4.      #
# ----------------------------------------------------------------------#

import argparse
import os
import subprocess
import signal
import time

TIMEOUT = 3

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


def crash_detector(rc):
  # A simple example for detect crash bugs
  if rc.returncode < 0 and -rc.returncode == signal.SIGSEGV:
    print("DETECTOR: Crash detected")
    exit(rc.returncode)


# Global vars for perf bug detector
avg_time = 0.0
iteration = 0

def performance_bug_detector(rc, exec_time, avg_exec_time, timeout):
  # Add performance bug detector logic here
  global avg_time
  t = avg_exec_time + timeout
  avg_time = (avg_time * (iteration - 1) + exec_time) / iteration # Update average: (oldAvg * oldCount + newVal) / newCount
  
  if iteration > 10 and exec_time >= t:
    print("DETECTOR: Performance bug detected. Timeout: {:.3f} seconds.\n".format(t))
    exit(rc.returncode)
  else:
    print("DETECTOR: Last execution time: {:.3f} seconds. Average execution time: {:.3f} seconds.\n".format(exec_time, avg_time))


def data_race_detector(args, m_env):
  # Add data race detector logic here
  dr_cmds = ["valgrind", "--tool=helgrind", "--error-exitcode=1"]

  res = subprocess.run(dr_cmds + args, env=m_env, capture_output=True)

  print(res.stdout.decode())
  print(res.stderr.decode())

  if res.returncode == 1:
    print("DETECTOR: Data race detected.\n")
    exit(res.returncode)


def memory_error_detector(args, m_env):
  # Add memory error detector logic here
  memory_cmds = ["valgrind", "--tool=memcheck", "--error-exitcode=1", "--leak-check=full"]

  res = subprocess.run(memory_cmds + args, env=m_env, capture_output=True)

  print(res.stdout.decode())
  print(res.stderr.decode())

  if res.returncode == 1:
    print("DETECTOR: Memory error detected.\n")
    exit(res.returncode)


if not os.path.exists("testlib.so"):
  print("testlib.so not found! Make sure to compile it with \"make library\"!")
  exit(1)

parser = argparse.ArgumentParser(description="Concurrent program testing")
parser.add_argument('-s', choices=["none", "pct", "random"], default="none", action="store", dest="algorithm")
parser.add_argument('-n', type=int, default=1, action="store", dest="iterations")
parser.add_argument('-st', type=str2bool, default=False, action="store", dest="stacktraces")
parser.add_argument('-seed', type=int, default=0, action="store", dest="seed")
parser.add_argument('-detector', type=str, required=False, dest='detector')
parser.add_argument("target", nargs="+", action="store")
args = parser.parse_args()

m_env = os.environ.copy()
m_env["STACKTRACES"] = str(args.stacktraces)
m_env["ALGORITHM"] = args.algorithm
m_env["LD_PRELOAD"] = "./testlib.so"

crash_det = False
perf_det = False
dr_det = False
memory_det = False

if args.detector and not set(args.detector.split(',')).issubset(["crash", "perf", "dr", "memory"]):
  raise argparse.ArgumentError('Invalid detector')
elif args.detector:
  for det in args.detector.split(','):
    if det == "crash":
      crash_det = True
    elif det == "perf":
      perf_det = True
    elif det == "dr":
      dr_det = True
    elif det == "memory":
      memory_det = True

exit_status = 0

for i in range(args.iterations):
  iteration += 1 # global
  m_env["SEED"] = str(args.seed + i)
  elapsed_time = 0.0
  
  if perf_det and i >= 10:
    start_time = time.monotonic()
    try:
      rc = subprocess.run(args.target, env=m_env, timeout=(avg_time + 3))
    except subprocess.TimeoutExpired:
      pass #Don't need to do anything here except stop execution, perf_bug_detector should see time elapsed timeout.
    end_time = time.monotonic()
    elapsed_time = (end_time - start_time) #time in fractional seconds
    performance_bug_detector(rc, elapsed_time, avg_time, TIMEOUT)
  else:
    start_time = time.monotonic()
    rc = subprocess.run(args.target, env=m_env)
    end_time = time.monotonic()
    if perf_det:
      elapsed_time = (end_time - start_time) #time in fractional seconds
      performance_bug_detector(rc, elapsed_time, avg_time, TIMEOUT)

  if rc.returncode > exit_status:
    exit_status = rc.returncode

  if crash_det:
    crash_detector(rc)

  if dr_det:
    data_race_detector(args.target, m_env)

  if memory_det:
    memory_error_detector(args.target, m_env)

exit(exit_status)
