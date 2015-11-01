#!/usr/bin/env python
from __future__ import print_function

import sys
import toolz as t
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

  
def op_counter(op):
  def num_ops(tree):
    if not isinstance(tree, list): return 0
    return (1 if tree[0] == op else 0) + sum(num_ops(c) for c in tree[1:])

  return num_ops


def flatten_function(f):
  #returns a new form
  def flattened_featurizer(tree):
    return f(flatten(tree))
  return flattened_featurizer


def mean_height_from_leaf(tree):
  if not isinstance(tree, list): return 0
  return mean(height_list(tree))


def min_height_tree_from_leaf(tree):
  if not isinstance(tree, list): return 0
  return min(height_list(tree))


def max_operation_depth(op):
  def ops_depth(tree):
    if not isinstance(tree, list): return 0
    return max(1 + depth(c) if c[0] == op else 0 + ops_depth(c) for c in tree[1:])
  return ops_depth


features = [ 
  (length.__name__, length),
  (num_nodes.__name__, num_nodes),
  (depth.__name__, depth), 
  ('num_normal', op_counter(':N')), 
  ('num_reverse', op_counter(':R')),
  (mean_height_from_leaf.__name__, mean_height_from_leaf),
  (min_height_tree_from_leaf.__name__, min_height_tree_from_leaf),
  ('reverse_max_depth', max_operation_depth(':R'))
]

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
