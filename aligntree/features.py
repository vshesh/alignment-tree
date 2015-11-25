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
    c += 1
    t += e
  return 0 if c is 0 else float(t)/c

def shifted_data_variance(data):
  # realize list. we're not dealing with anything big enough for this to matter.
  # In fact, I wouldn't be suprised if using generators is actually slower
  # for us.
  data = list(data)
  if len(data) < 2: return 0

  K = data[0]
  total = 0
  sqtotal = 0
  n = 0
  for x in data:
    n += 1
    total += x - K
    sqtotal += (x-K)*(x-K)
  # the n-1 at the end is for sample variance. use n for population variance.
  return (sqtotal - (total*total)/n)/(n-1)


def naive_variance(l):
  """
  This algorithm is very prone to catastrophic cancellation.
  If sqtotal and total are about the same, then we lose lots of precision
  in the calculation.
  """
  count = 0
  total = 0
  sqtotal = 0
  for e in l:
    count += 1
    total += e
    sqtotal += e**2

  return 0 if count < 2 else math.sqrt((sqtotal - total)/(count-1))

stdev = lambda l: math.sqrt(shifted_data_variance(l))

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


def in_order(tree):
  if not isinstance(tree, list):
    return tree
  return list(flatten(list(t.interpose(tree[0], map(in_order, tree[1:])))))


def unzip(path, tree):
  if not hasattr(tree, '__iter__'): 
    yield path + [tree]
  else:
    for p in t.mapcat(t.partial(unzip, path + tree[0:1]), tree[1:]):
      yield p

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
    return t.pipe(tree,
                  flatten,
                  tc.filter(lambda x: extract_op(x) == op),
                  t.count)

  return num_ops


def mean_height_from_leaf(tree):
  if not isinstance(tree, list): return 0
  return mean(height_list(tree))

def stdev_height_from_leaf(tree):
  if not isinstance(tree, list): return 0
  return stdev(height_list(tree))


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


def mean_x_pos_R_in_tree(tree):
  traversal = in_order(tree)
  x_pos = [x[0] for x in enumerate(traversal) if ':R' in x[1]]
  return mean(x_pos)


def stdev_x_pos_R_in_tree(tree):
  traversal = in_order(tree)
  x_pos = [x[0] for x in enumerate(traversal) if ':R' in x[1]]
  return stdev(x_pos)


def markov_tables(tree):
  result = {}
  # for orders 1 and 2:
  for order in xrange(1, 3):
    keySet, averages = set(), {}
    # process the initial sliding window to just contain N/R's
    paths = [list(list(_.split('^')[0][1] if ':' in _ else _ for _ in elem) \
      for elem in t.sliding_window(order, path)) \
      for path in list(unzip([], tree))]
    for i in xrange(len(paths)):
      order_counter = {}
      for window in paths[i]:
        if window[len(window) - 1] == 'R' or window[len(window) - 1] == 'N':
          if ''.join(window) in order_counter:
            order_counter[''.join(window)] += 1
          else:
            order_counter[''.join(window)] = 1
            keySet.add(''.join(window))
      total = float(sum(list(order_counter.itervalues())))
      if total > 0:
        for key in order_counter:
          order_counter[key] = float(order_counter[key]) / total
      # save the number of operations to original list
      paths[i] = order_counter
    # omit any empty paths
    paths = [path for path in paths if len(path) > 0]
    # combine all the probabilities from the different paths
    for key in keySet:
      for path in paths:
        if key in averages and key in path:
          averages[key] += path[key]
        elif key in path:
          averages[key] = path[key]
      # divide by number of paths to get final result
      averages[key] = float(averages[key]) / float(len(paths))
    result.update(averages)
  # update result to have new keys with 'markov_'
  keys = result.keys()
  for key in keys: 
    result['markov_' + key] = str(result[key])
    del result[key]
  return result


features = [
  ('length', length),
  ('num_nodes', num_nodes),
  ('depth', depth),
  ('num_normal', op_counter(':N')),
  ('num_reverse', op_counter(':R')),
  ('max_range_reverse', op_range(max, ':R')),
  ('min_range_reverse', op_range(min, ':R')),
  ('mean_range_reverse', op_range(mean, ':R')),
  ('stdev_range_reverse', op_range(stdev, ':R')),
  ('mean_height_from_leaf', mean_height_from_leaf),
  ('stdev_height_from_leaf', stdev_height_from_leaf),
  ('min_height_tree_from_leaf', min_height_tree_from_leaf),
  ('reverse_max_depth', max_operation_depth(':R')),
  ('mean_x_pos_R_in_tree', mean_x_pos_R_in_tree),
  ('stdev_x_pos_R_in_tree', stdev_x_pos_R_in_tree),
]

# add compressed versions of the features.
features += [('compressed_' + x[0], t.compose(x[1], compress))
             for x in features]


if __name__ == '__main__':

  markov_features = ['markov_N', 'markov_R', 'markov_NR', 'markov_RN', 'markov_NN', 'markov_RR']
  opts, args = getopt.getopt(sys.argv[1:], 'l:', ['--language'])
  language = None
  for o,a in opts:
    if o == '-l' or o == '--language':
      language = a + ','

  print(('language,' if language is not None else '') +
         ','.join(x[0] for x in features) + ',' + 
          ','.join(markov_features) + ',' +
          ','.join([('compressed_' + f) for f in markov_features]))

  for line in fileinput.input(args):
    tree = parse_sexp(line)[0]
    print( (language or '') + ','.join([str(f[1](tree)) for f in features] + 
      list(t.get(markov_features, markov_tables(tree), str(0.0))) + 
      list(t.get(markov_features, markov_tables(compress(tree)), str(0.0)))))
