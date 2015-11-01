#!/usr/bin/env python
from __future__ import print_function

import sys
import toolz as t
import toolz.curried as tc
import fileinput
import getopt

# --------------------------- I/O Utilities ------------------------------
#Sample Usage:
#>>> parse_sexp("(+ 5 (+ 3 5))")
#[['+', '5', ['+', '3', '5']]]
def parse_sexp(string):
  sexp = [[]]
  word = ''
  in_str = False
  for c in string:
    if c == '(' and not in_str:
      sexp.append([])
    elif c == ')' and not in_str:
      if(len(word) > 0):
        sexp[-1].append(word)
        word = ''
      temp = sexp.pop()
      sexp[-1].append(temp)
    elif c in (' ', '\n', '\t') and not in_str:
      if len(word) > 0:
        sexp[-1].append(word)
        word = ''
    elif c == '\"':
      in_str = not in_str
    else:
      word = word + c
  return sexp[0]


def dumptree(tree):
    if (tree == None): return ''
    if not isinstance(tree, list): return str(tree)
    return '('+tree[0]+' '+ ' '.join(dumptree(child) for child in tree[1:]) + ')'


def mean(int_list):
  #converts list into a mean
  return sum(int_list)/float(len(int_list))

# ------------------------ Transformations -----------------------------------

def flatten(sexp):
  if sexp is None: return None
  if not isinstance(sexp, list): return sexp
  if all(not isinstance(x, list) for x in sexp): return sexp

  # if both heads are the same then gut the children.
  children = list(map(flatten, sexp[1:]))
  heads = set(t.pluck(0, filter(lambda x: isinstance(x,list),children)))
  heads.add(sexp[0])
  # number heads are fine, we just want to make sure that the
  # string type heads are all the same
  if len(heads) <= 1:
    return list(t.cons(sexp[0], t.concat(x[1:] if isinstance(x,list) else [x] 
                                         for x in children)))

  return [sexp[0]]+children

def flatten_list(l):
  for x in l:
    if not isinstance(x, list): yield x
    else:
      for e in flatten_list(x):
        yield e

def group_by_op(tree):
  return t.pipe(tree, 
    flatten_list, 
    tc.filter(lambda e: isinstance(e, str)),
    tc.groupby(lambda e: e.split('^')[0]), 
    dict)

def height_list(tree):
  #return a list of all the heights in a tree from the leaf nodes
  if not isinstance(tree, list): return [0]
  return [x+1 for x in t.concat(height_list(c) for c in tree[1:])]


# ----------------------- Features -------------------------------------------

def length(tree):
  if not isinstance(tree, list): return tree
  return max(length(c) for c in tree[1:])

  
def depth(tree):
  if not isinstance(tree, list): return 0
  return 1 + max(depth(x) for x in tree[1:])


def num_nodes(tree):
  if not isinstance(tree, list): return 0
  return 1 + sum(num_nodes(c) for c in tree[1:])


def op_range(func, op):
  def helper(tree):
    if not isinstance(tree, list): return 0
    groups = group_by_op(tree)
    return func((lambda e: int(e[1]) - int(e[0]))(i.split('^')[1].split('-')) for i in (groups[op] if op in groups else [':^0-0']))
  return helper


def mean_range(tree):
  if not isinstance(tree, list): return 0


  
def op_counter(op):
  def num_ops(tree):
    if not isinstance(tree, list): return 0
    return (1 if tree[0].split('^')[0] == op else 0) + sum(num_ops(c) for c in tree[1:])

  return num_ops


def flatten_function(f):
  #returns a new form
  def flattened_featurizer(tree):
    return f(flatten(tree))
  return flattened_featurizer

op_types = ['N', 'R', '4one', '4two', 
            '5one', '5two', '5three', 
            '5four', '5five', '5six', 
            '6n1', '6n2', '6n3', '6n4', 
            '6n5', '6n6', '6n7', '6n8',
            '6n9', '6n10', '6n11', '6n12', 
            '6n13', '6n14', '6n15', '6n16', 
            '6n17', '6n18', '6n19', '6n20', 
            '6n21', '6n22', '6n23', '6n24', 
            '6n25', '6n26', '6n27', '6n28', 
            '6n29', '6n30', '6n31', '6n32', 
            '6n33', '6n34', '6n35', '6n36', 
            '6n37', '6n38', '6n39', '6n40', 
            '6n41', '6n42', '6n43', '6n44', 
            '6n45', '6n46']

def mean_height_from_leaf(tree):
  if not isinstance(tree, list): return 0
  return mean(height_list(tree))


def min_height_tree_from_leaf(tree):
  if not isinstance(tree, list): return 0
  return min(height_list(tree))


# def max_operation_depth(op):
#   def ops_depth(tree):
#     if not isinstance(tree, list): return 0

#     return max( 1 + ops_depth(c) for c in tree[1:] if c[0])


features = [ 
  (length.__name__, length),
  (num_nodes.__name__, num_nodes),
  (depth.__name__, depth),
  ('max_range_reverse', op_range(max, ':R')),
  ('min_range_reverse', op_range(min, ':R')),
  ('num_normal', op_counter(':N')), 
  ('num_reverse', op_counter(':R')),
  (mean_height_from_leaf.__name__, mean_height_from_leaf),
  (min_height_tree_from_leaf.__name__, min_height_tree_from_leaf)
]

# features += [(('num_' + op_type), op_counter(':' + op_type)) for op_type in op_types]

# Flatten featurizers and add them
features += [('flattened_' + i[0], flatten_function(i[1])) for i in features]


if __name__ == '__main__':

  opts, args = getopt.getopt(sys.argv[1:], 'l:', ['--language'])
  language = None
  for o,a in opts:
    if o == '-l' or o == '--language':
      language = a + ','
  
  print(('language,' if language is not None else '') + 
        ','.join(x[0] for x in features))
  
  for line in fileinput.input(args):
    tree = parse_sexp(line)[0]
    print( (language or '') + ','.join(
      str(f[1](tree)) for f in features))
