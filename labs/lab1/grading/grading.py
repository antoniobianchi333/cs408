#!/usr/bin/env python3
#
# Overwrite libunwind and  Makefile
#
#  $ overwrite.py
#  
# Sperate the students in two diff groups, and run:
#   
#  $ python3 -u grading.py &> log.txt
#
# This will run:
#   - students testcases
#   - ta test cases within ta_test_cases
# And generate json file in student's dir

import sys
import os
import subprocess
import random
import json

STUDENTS_ROOT_DIR = "students_A"
#STUDENTS_ROOT_DIR = "students_B"
#STUDENTS_ROOT_DIR = "testing"
GRADING = None

def do_work(log_file, cmd):
    """
    Runs a command and treats success and timeout outcomes as normal.

    - Merges stdout and stderr into a single stream.
    - On success or timeout, appends the output to the log file and returns it.
    - On any other error, returns None.
    """
    output_content = None

    try:
        # Run the command, capturing the merged output in memory.
        # - stdout=subprocess.PIPE: Captures standard output.
        # - stderr=subprocess.STDOUT: Redirects standard error to standard output.
        # - text=True: Decodes the output as a string (for the success case).
        # - check=True: Raises CalledProcessError if the command returns a non-zero code.
        pr = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=900,
            check=True
        )
        # If the command succeeds, the merged output is a string in pr.stdout.
        output_content = pr.stdout

    except subprocess.TimeoutExpired as e:
        # This is a normal outcome. The captured output (e.stdout) is in BYTES.
        print(f"[script] Command timed out (handled as normal): {' '.join(cmd)}")
        if e.stdout:
            # We must DECODE the bytes into a string before writing or returning.
            output_content = e.stdout.decode('utf-8', errors='replace')
        else:
            output_content = "" # Ensure we have a string even if no output was captured.

    except Exception as e:
        # Any other exception (like CalledProcessError) is a failure.
        print(f"[script] An error occurred, returning None: {e}")
        return None

    # This code runs for both success and timeout cases.
    try:
        # Append the captured content to the log file.
        with open(log_file, "a") as outfile:
            outfile.write(output_content)
        # Return the captured content.
        return output_content
    except IOError as e:
        print(f"[script] Error writing to log file {log_file}: {e}")
        return None


def detector(students_dir, log_file):
    if os.path.exists(log_file):
        os.remove(log_file)
    content = do_work(log_file, ["make", "run_dectector_tests"])

    if content:
        if "DETECTOR: Crash detected" in content:
            print("Crash correct in random")
            GRADING["students_detector"]["crash"] += 9
        if "DETECTOR: Memory error detected" in content:
            print("Memory correct in random")
            GRADING["students_detector"]["mem"] += 9
        if "DETECTOR: Data race detected" in content:
            print("dr correct in random")
            GRADING["students_detector"]["dr"] += 9
        if "DETECTOR: Performance bug detected. Timeout" in content:
            print("perf correct in random")
            GRADING["students_detector"]["perf"] += 9


def ta_detector(students_dir, log_file):
    if os.path.exists(log_file):
        os.remove(log_file)
    content = do_work(
        log_file,
        [
            "python3",
            "framework.py",
            "-s",
            "random",
            "-n",
            "5",
            "-st=false",
            "-seed=10",
            "-detector=dr,crash,memory,perf",
            "ta_test_cases/crash",
        ],
    )

    if content:
        if "DETECTOR: Crash detected" in content:
            print("Crash correct in random")
            GRADING["ta_detector"]["crash"] += 1
        if "DETECTOR: Memory error detected" in content:
            print("Memory correct in random")
            GRADING["ta_detector"]["mem"] += 1
        if "DETECTOR: Data race detected" in content:
            print("dr correct in random")
            GRADING["ta_detector"]["dr"] += 1
        if "DETECTOR: Performance bug detected. Timeout" in content:
            print("perf correct in random")
            GRADING["ta_detector"]["perf"] += 1

    content = do_work(
        log_file,
        [
            "python3",
            "framework.py",
            "-s",
            "random",
            "-n",
            "100",
            "-st=false",
            "-seed=1",
            "-detector=perf",
            "ta_test_cases/perf",
        ],
    )

    if content:
        if "DETECTOR: Crash detected" in content:
            print("Crash correct in random")
            GRADING["ta_detector"]["crash"] += 1
        if "DETECTOR: Memory error detected" in content:
            print("Memory correct in random")
            GRADING["ta_detector"]["mem"] += 1
        if "DETECTOR: Data race detected" in content:
            print("dr correct in random")
            GRADING["ta_detector"]["dr"] += 1
        if "DETECTOR: Performance bug detected. Timeout" in content:
            print("perf correct in random")
            GRADING["ta_detector"]["perf"] += 1


def coverages(students_dir, log_file):
    cmd = ["make", "run_coverage_tests"]

    if os.path.exists(log_file):
        os.remove(log_file)

    if do_work(log_file, cmd):
        GRADING["students_coverages"] += 50


def sched_none(students_dir, log_file):
    cmd = [
        "python3",
        "framework.py",
        "-s",
        "none",
        "-n",
        "1",
        "-st=false",
        "-seed=10",
        "ta_test_cases/argument_test",
    ]

    if os.path.exists(log_file):
        os.remove(log_file)

    if do_work(log_file, cmd):
        GRADING["sched_none"] += 10


def sched_rand(students_dir, log_file):
    cmd = [
        "python3",
        "framework.py",
        "-s",
        "random",
        "-n",
        "1",
        "-st=false",
        "-seed=10",
        "ta_test_cases/random_test",
    ]

    if os.path.exists(log_file):
        os.remove(log_file)

    do_work(log_file, cmd)

    # See the random_test.c
    content = "----------- OUTPUT ------------\n"
    try:
        with open("output.txt", "r") as f:
            content += f.read()
        GRADING["sched_rand"] += 20
    except Exception as e:
        note = f"[script] output.txt not found, sched_rand failed"
        print(note)
        content += f"{note}\n"

    with open(log_file, "a") as f:
        f.write(content)


def run_cmd(cmd):
    print(f"[script] Run: {cmd}")
    rc = subprocess.run(
        cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    print(rc.stdout)


def init_students(students_dir):
    try:
        run_cmd(["make", "clean"])
        run_cmd(["make", "library"])
        GRADING["framework_testlib_build"] = 20
    except subprocess.CalledProcessError as e:
        print(f"[script] STDOUT: {e.stdout}")
        return 1
    return 0


# DIR:
#    <root>:
#          |-students
#          |-ta_test_cases
#
def main():
    global GRADING

    # students = "group_123"
    for students in os.listdir(STUDENTS_ROOT_DIR):
        GRADING = {
            # 100 points
            # Check output manually
            "framework_testlib_build": 0,  # 20
            "students_coverages": 0,  # 50
            "sched_none": 0,  # 10
            "sched_rand": 0,  # 20
            # 40 points
            "students_detector": {
                "dr": 0,
                "perf": 0,
                "crash": 0,
                "mem": 0,
            },  # 9 + 9 + 9 + 9
            "ta_detector": {
                "dr": 0,
                "perf": 0,
                "crash": 0,
                "mem": 0,
            },  # 1 + 1 + 1 + 1
        }

        orig_cwd = os.getcwd()
        ta_tests_dir = os.path.join(orig_cwd, "ta_test_cases")

        students = os.path.join(STUDENTS_ROOT_DIR, students)

        os.chdir(students)
        print(f"\n--------------------------------------------\n")
        print(f"[script] pushd: {students}")
        print(f"[script] TA test cases: {ta_tests_dir}")
        run_cmd(["cp", "-r", f"{ta_tests_dir}", "."])
        run_cmd(["make", "-C", "ta_test_cases", "all"])

        # 1. Rerun students tests cases
        if init_students(students):
            print(f"[script] Cannot build the testlib")
            grading_output = "grading.json"
            with open(grading_output, "w") as f:
                f.write(json.dumps(GRADING))
            os.chdir(orig_cwd)
            print(
                f"[script] popd: {orig_cwd}\n---------------------------------------\n"
            )
            continue
        print("[script] Run students test cases")
        coverages(students, "grading_coverage_student_cases.out")

        # 2. Run our test cases
        init_students(students)
        print("[script] Run TA test cases")
        sched_none(students, "grading_sched_none.out")
        sched_rand(students, "grading_sched_rand.out")

        # 3. Run students detector cases
        init_students(students)
        print("[script] Run student detector cases")
        detector(students, "grading_detector_student_cases.out")

        # 4. Run our test cases
        init_students(students)
        print("[script] Run TA detector cases")
        ta_detector(students, "grading_detector_ta_cases.out")

        grading_output = "grading.json"
        with open(grading_output, "w") as f:
            f.write(json.dumps(GRADING, indent=4))

        os.chdir(orig_cwd)
        print(f"[script] popd: {orig_cwd}\n---------------------------------------\n")


main()
