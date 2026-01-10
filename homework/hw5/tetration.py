import sys

sys.set_int_max_str_digits(100000)

def tetration(n):
  base = 2
  total = 0
  for i in range(n + 1):
    total = base ** total
    print("\t", i, total)
  return total

print(tetration(1))
print(tetration(2))
print(tetration(3))