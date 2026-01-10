from typing import List, Set, Dict, Any
from copy import deepcopy
"""
Simple path: 
  - if no node appears more than once in the path, except that the first and last nodes may be the same
  - No internal loops
  - Can bound their length
  - Can create any path by composing simple paths
  - Many simple paths exist for most programs

Prime path
  -  a path is prime if it is simple and does not appear as a proper subpath of any other simple path
  - Simple path of maximal length

"""
# EDGES
# Key: Node
# Value: Set of outgoing destination nodes

# https://www.cs.virginia.edu/~up3f/cs3250/supplement/Prime-Path-Coverage.pdf
# EDGES: Dict[int, Set[int]] = {
#   1 : {2},
#   2 : {3, 4},
#   3 : {2},
#   4 : {}
# }

# quiz2 old cfg0
# EDGES: Dict[int, Set[int]] = {
#   1 : {2, 7},
#   2 : {3, 4},
#   3 : {2},
#   4 : {5, 6},
#   5 : {6},
#   6 : {1},
#   7 : {}
# }

# hw2 new q1
EDGES: Dict[int, Set[int]] = {
  1 : {2, 3},
  2 : {8},
  3 : {4, 8},
  4 : {5, 6},
  5 : {7},
  6 : {7},
  7 : {3},
  8 : {}
}

def is_ordered_sublist(sublist: List[Any], list: List[Any]) -> bool:
  assert(len(sublist) > 0)
  sublist_idx = 0
  sublist_len = len(sublist)

  for ele in list:
    # Update the index in the sublist to compare
    if ele == sublist[sublist_idx]:
      sublist_idx += 1
    # reset the sublist start
    else:
      sublist_idx = 0
    
    # Terminate if the length is the end of the sublist
    if sublist_idx == sublist_len:
      return True
  return False

def add_pp(curr_path: List[int], paths: List[List[int]], simple: bool=False) -> None:
  """
  Does not add if the length of curr_path is 1 (aka no edges)

  If "simple" is True generate simple paths

  Otherwise generate prime paths
  Adds path if
    - Not already in it (set behavior)
    - if curr_path not subpath in any path
  """
  assert(len(curr_path) >= 1)
  if(len(curr_path) == 1):
    return
  if simple:
    if curr_path not in paths:
      paths.append(curr_path)
  else:
    if not is_ordered_sublist(curr_path, paths):
      if curr_path not in paths:
        paths.append(curr_path)


def gen_pp_for_node(curr_node: int, curr_path: List[int], paths: List[List[int]], edges: Dict[int, Set[int]], simple: bool) -> List[List[int]]:
  # A prime path path may start and end in the same node
  if len(curr_path) >= 2 and curr_path[0] == curr_node and curr_path[-1] == curr_node:
    add_pp(curr_path, paths, simple)
    return paths
  # Terminate if node already exists and is not the same as
  # the start node.  To create a path of [1, 1] it will fall through to the append
  elif len(curr_path) >= 1 and curr_path[0] != curr_node and curr_node in curr_path:
    add_pp(curr_path, paths, simple)
    return paths

  # Add curr node to path
  curr_path.append(curr_node)

  # Otherwise check if it is possible to add a node
  paths_old_copy = deepcopy(paths)
  curr_path_old_copy = deepcopy(curr_path)
  paths_old = deepcopy(paths)
  curr_path_old = deepcopy(curr_path)
  
  # Terminate here if first and last are the same
  if len(curr_path) >= 2 and curr_path[0] == curr_path[-1]:
    add_pp(curr_path, paths, simple)
  # Curr node has more outgoing edges
  elif len(edges[curr_node]) > 0:
    for next_node in edges[curr_node]:
      next_paths = gen_pp_for_node(next_node, curr_path_old, paths_old, edges, simple)

      paths_old = deepcopy(paths_old_copy)
      curr_path_old = deepcopy(curr_path_old_copy)
      
      for np in next_paths:
        add_pp(np, paths, simple)
  # Has no more outgoing
  else:
    add_pp(curr_path, paths, simple)

  return paths

def remove_sub_paths(pps: List[List[int]]) -> List[List[int]]:
  """
  Due to the order things are parsed there may be still sub paths
  Delete them here
  """
  ret: List[List[int]] = []

  for path1 in pps:
    add = True
    for path2 in pps:
      if path1 == path2:
        continue
      if is_ordered_sublist(path1, path2):
        add = False
    if add:
      add_pp(path1, ret)
  return ret

def gen_ppc_tr(edges: Dict[int, Set[int]], simple: bool) -> Dict[int, List[List[int]]]:
  pps: List[List[int]] = []
  for node in edges.keys():
    pp = gen_pp_for_node(node, [], [], edges, simple)
    for p in pp:
      add_pp(p, pps, simple)
  
  # Purge subpaths if we are looking for prime paths
  if not simple:
    pps = remove_sub_paths(pps)
  return pps

if __name__ == "__main__":
  print("Generating all prime paths")
  pps: List[List[int]] = gen_ppc_tr(EDGES, False)

  for pp in pps:
    print(pp)

  print(len(pps))

  print("Generating all simple paths")
  sps: List[List[int]] = gen_ppc_tr(EDGES, True)

  for sp in sps:
    print(sp)

  print(len(sps))