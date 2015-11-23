#!/usr/bin/env python
from __future__ import print_function

import sys
import math
import toolz as t
import toolz.curried as tc
import fileinput
import getopt

# -------------------------- GENERAL UTILITIES -----------------------------
def mean(l):
  t = 0
  c = 0
  for e in l:
    c+= 1
    t += e
  return float(t)/c


def std_dev(l):
  avg = mean(l)
  variance = map(lambda x: (x - avg)**2, l)
  return math.sqrt(mean(variance))


extract_op = lambda s: s.split('^')[0]
extract_range = lambda s: list(map(int, s.split('^')[1].split('-')))
extent = lambda r: r[1]-r[0]


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

# ------------------------ Transformations -----------------------------------

def compress(sexp):
  if sexp is None: return None
  if not isinstance(sexp, list): return sexp
  if all(not isinstance(x, list) for x in sexp): return sexp

  # if both heads are the same then gut the children.
  children = list(map(compress, sexp[1:]))
  heads = set(extract_op(x) for x in t.pluck(0, filter(lambda x: isinstance(x,list),children)))
  heads.add(extract_op(sexp[0]))
  # number heads are fine, we just want to make sure that the
  # string type heads are all the same
  if len(heads) <= 1:
    return list(t.cons(sexp[0], t.concat(x[1:] if isinstance(x,list) else [x]
                                         for x in children)))

  return [sexp[0]]+children


def flatten(l):
  for x in l:
    if not isinstance(x, list): yield x
    else:
      for e in flatten(x):
        yield e


def group_by_op(tree):
  return t.pipe(tree,
    flatten,
    tc.filter(lambda e: isinstance(e, str)),
    tc.groupby(lambda e: e.split('^')[0]),
    dict)


def height_list(tree):
  # return a list of all the heights in a tree from the leaf nodes
  # it's the same as all the depths to the leaf nodes from the root.
  if not isinstance(tree, list): return [0]
  return [x+1 for x in t.concat(height_list(c) for c in tree[1:])]


# ----------------------- Features -------------------------------------------

# # this is a little more computationally intensive than we need.
# def length(tree):
#   if not isinstance(tree, list): return int(tree)
#   return max(length(c) for c in tree[1:])

# thanks to our new more complete output format.
def length(tree):
  return int(tree[0].split('^')[1].split('-')[1])


def depth(tree):
  if not isinstance(tree, list): return 0
  return 1 + max(depth(x) for x in tree[1:])


# note that num_nodes(original tree) = length(original tree)
# this is only interesting for flattened trees.
def num_nodes(tree):
  return t.pipe(tree,
                flatten,
                tc.filter(lambda x: x.startswith(':')),
                t.count)


def op_range(func, op):
  def helper(tree):
    if not isinstance(tree, list): return 0
    return t.pipe(group_by_op(tree),
                  lambda groups: groups[op] if op in groups else [':^0-0'],
                  lambda x: func(extent(extract_range(i)) for i in x))
  return helper


def op_counter(op):
  def num_ops(tree):
    if not isinstance(tree, list): return 0
    return (1 if tree[0].split('^')[0] == op else 0) + sum(num_ops(c) for c in tree[1:])

  return num_ops


def mean_height_from_leaf(tree):
  if not isinstance(tree, list): return 0
  return mean(height_list(tree))

def std_dev_height_from_leaf(tree):
  if not isinstance(tree, list): return 0
  return std_dev(height_list(tree))


def min_height_tree_from_leaf(tree):
  if not isinstance(tree, list): return 0
  return min(height_list(tree))


def max_operation_depth(op):
  def ops_depth(tree):
    if not isinstance(tree, list): return 0
    if extract_op(tree[0]) == op:
      return depth(tree)
    return max( ops_depth(c) for c in tree[1:])
  return ops_depth


features = [
  ('length', length),
  ('num_nodes', num_nodes),
  ('depth', depth),
  ('num_normal', op_counter(':N')),
  ('num_reverse', op_counter(':R')),
  ('max_range_reverse', op_range(max, ':R')),
  ('min_range_reverse', op_range(min, ':R')),
  ('mean_range_reverse', op_range(mean, ':R')),
  ('std_dev_range_reverse', op_range(std_dev, ':R')),
  ('mean_height_from_leaf', mean_height_from_leaf),
  ('std_dev_height_from_leaf', std_dev_height_from_leaf),
  ('min_height_tree_from_leaf', min_height_tree_from_leaf),
  ('reverse_max_depth', max_operation_depth(':R')),
]


# add compressed versions of the features.
features += [('compressed_' + x[0], t.compose(x[1], compress))
             for x in features]


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
