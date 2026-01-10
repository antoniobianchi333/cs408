L = ["(A, 1, x)", "(A, 1, y)", "(A, 2, x)", "(A, 2, y)", \
     "(A, 3, x)", "(A, 3, y)", "(B, 1, x)", "(B, 1, y)", \
      "(B, 2, x)", "(B, 2, y)", "(B, 3, x)", "(B, 3, y)"]

l = sorted(L)
for item in l:
  item_str = str(item)
  item_str = item_str.replace("\"", "")
  item_str = item_str.replace("[", "")
  item_str = item_str.replace("]", "")
  print(item_str)