import os

for student in os.listdir("students_A"):
    print(f" students_A/{student}/testlib.c", end='')

for student in os.listdir("students_B"):
    print(f" students_B/{student}/testlib.c", end='')

print("")

for student in os.listdir("students_A"):
    print(f" students_A/{student}/framework.py", end='')

for student in os.listdir("students_B"):
    print(f" students_B/{student}/framework.py", end='')


print("")
