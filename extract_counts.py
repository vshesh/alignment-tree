#!/bin/python

# File: extract_counts.bash
# Author: Vishesh Gupta
# 
# Takes a non-min json file that has a bunch of parse trees 
# and tries to extract relevant features. 
# 
# So far the features it will extract are:
# 1. Counts of the occurrences of each operation. 
# 2. Depth - the depth of the tree is defined as follows:
#   For each operation node, if the node's only children are the same operation
#   or a terminal value (so an actual word), then the depth is ignored.
#   
#   Basically what this means is that only transitions of operations (so a 
#   normal with a child that is a reverse) or nodes with two operations as
#   children count for depth.
#   
#   It's a little more complicated when there are more than 2 chidren. 
#   for now, since in general it seems that the apprearance of such operations
#   is rare, we will say that all operations > length 2 count towards the depth
#   

import sys
import json
import re

operations = {
    2: {(0,1): 'N', (1,0): 'R'},
    4: {(1,3,0,2): '4one', (2,0,3,1): '4two'}, 
    5: {(1,3,0,4,2): '5one', 
        (1,4,2,0,3): '5two', 
        (2,0,4,1,3): '5three', 
        (2,4,0,3,1): '5four', 
        (3,0,2,4,1): '5five', 
        (3,1,4,0,2): '5six'
    },
    6: {(1, 3, 0, 5, 2, 4): '6n1', 
        (1, 3, 5, 0, 2, 4): '6n2', 
        (1, 3, 5, 0, 4, 2): '6n3', 
        (1, 3, 5, 2, 0, 4): '6n4', 
        (1, 4, 0, 2, 5, 3): '6n5', 
        (1, 4, 0, 3, 5, 2): '6n6', 
        (1, 4, 2, 0, 5, 3): '6n7', 
        (1, 4, 2, 5, 0, 3): '6n8', 
        (1, 5, 2, 4, 0, 3): '6n9', 
        (1, 5, 3, 0, 2, 4): '6n10', 
        (1, 5, 3, 0, 4, 2): '6n11', 
        (2, 0, 3, 5, 1, 4): '6n12', 
        (2, 0, 4, 1, 5, 3): '6n13', 
        (2, 0, 5, 3, 1, 4): '6n14', 
        (2, 4, 0, 3, 5, 1): '6n15', 
        (2, 4, 0, 5, 1, 3): '6n16', 
        (2, 4, 0, 5, 3, 1): '6n17', 
        (2, 4, 1, 5, 0, 3): '6n18', 
        (2, 5, 0, 3, 1, 4): '6n19', 
        (2, 5, 0, 4, 1, 3): '6n20', 
        (2, 5, 1, 3, 0, 4): '6n21', 
        (2, 5, 1, 4, 0, 3): '6n22', 
        (2, 5, 3, 0, 4, 1): '6n23', 
        (3, 0, 2, 5, 1, 4): '6n24', 
        (3, 0, 4, 1, 5, 2): '6n25', 
        (3, 0, 4, 2, 5, 1): '6n26', 
        (3, 0, 5, 1, 4, 2): '6n27', 
        (3, 0, 5, 2, 4, 1): '6n28', 
        (3, 1, 4, 0, 5, 2): '6n29', 
        (3, 1, 5, 0, 2, 4): '6n30', 
        (3, 1, 5, 0, 4, 2): '6n31', 
        (3, 1, 5, 2, 0, 4): '6n32', 
        (3, 5, 0, 2, 4, 1): '6n33', 
        (3, 5, 1, 4, 0, 2): '6n34', 
        (3, 5, 2, 0, 4, 1): '6n35', 
        (4, 0, 2, 5, 1, 3): '6n36', 
        (4, 0, 2, 5, 3, 1): '6n37', 
        (4, 0, 3, 1, 5, 2): '6n38', 
        (4, 1, 3, 0, 5, 2): '6n39', 
        (4, 1, 3, 5, 0, 2): '6n40', 
        (4, 1, 5, 2, 0, 3): '6n41', 
        (4, 1, 5, 3, 0, 2): '6n42', 
        (4, 2, 0, 3, 5, 1): '6n43', 
        (4, 2, 0, 5, 1, 3): '6n44', 
        (4, 2, 0, 5, 3, 1): '6n45',
        (4, 2, 5, 0, 3, 1): '6n46' 
    }
}

def extract_name_counts(successful, onames):
  return [(name, len(re.findall(name+'\\(', json.dumps(successful))) ) for name in onames]


def depth(parse_tree):
  if parse_tree is None: return 0

  operation = parse_tree['name'].split('(')[0]
  depthcondition = False
  children = 0
  if 'children' in parse_tree: 
    # get the children depth
    children = sum([depth(child) for child in parse_tree['children']])
    nonterminals = 0
    for child in parse_tree['children']:
      childoperation = child['name'].split('(')[0]
      if not childoperation.isdigit():
        nonterminals += 1
        if childoperation is not operation or nonterminals > 1:
          depthcondition = True
          break

  return (1 if depthcondition else 0) + children


def terminals(parse_tree):
  if 'children' not in parse_tree:
    return [parse_tree['name']]
  l = []
  for c in parse_tree['children']:
    l.extend(terminals(c))
  return l

def length(parse_tree):
  return max(map(lambda x: int(x), terminals(parse_tree))) + 1

def origlength(alignment):
  return max(map(lambda x: int(x.split('-')[1]), alignment.split())) + 1

if __name__ == '__main__':
  # extract the names of all the operations from the array.
  operation_names = []
  for item in operations.items():
    operation_names.extend(map(lambda x: x[1], item[1].items()))

  f = open(sys.argv[1])
  j = json.load(f)
  successful = filter(lambda x: True if x['success']=='yes' else False,  j)
  print extract_name_counts(successful, operation_names)
  depths = [[length(x['parse_tree']), depth(x['parse_tree'])] for x in successful]
  print str(depths).replace('[', '{').replace(']','}')











