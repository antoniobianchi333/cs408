import sys
import os
import subprocess
import random
import json

def main():
    STUDENTS_ROOT_DIR = "students"

    # students = "group_123"
    for students in os.listdir(STUDENTS_ROOT_DIR):

        print(f"[script] DIR: {students}")

        student_dir = os.path.join(STUDENTS_ROOT_DIR, students)
        if not os.path.isdir(student_dir):
            continue
        if not students.startswith("group"):
            continue

        cmd = ["cp", "Makefile", f"{student_dir}/."]
        print(f"[script] Run {cmd}")
        subprocess.run(cmd)

        cmd = ["cp", "-r", "libunwind", f"{student_dir}/."]
        print(f"[script] Run {cmd}")
        subprocess.run(cmd)

main()
