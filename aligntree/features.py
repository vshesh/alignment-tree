#!/usr/bin/env python
from __future__ import print_function

import sys
import math
import toolz as t
import toolz.curried as tc
import fileinput
import getopt
from collections import defaultdict as dd

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
  if isinstance(tree, str) or not hasattr(tree, '__iter__'):
    yield path + [tree]
  else:
    for p in t.mapcat(t.partial(unzip, path + tree[0:1]), tree[1:]):
      yield p


# another markov implementation (maybe a bit more generalized?)
# leaving it here for reference

# def markov(order, chain):
#   events = list(t.sliding_window(order+1, chain))
#   boxes = t.reduceby(lambda x: x[:-1], lambda acc,x:acc+1, events,init=0)
#   return dd(lambda: 0.0,
#             t.itemmap(lambda x: ('-'.join(x[0]), float(x[1])/boxes[x[0][:-1]]),
#                       t.frequencies(events)))

# def aggregate_markov_tables(order, ops, agf):
#   def markov_aggregator(tree):
#     return t.pipe(unzip([], tree),
#                   tc.map(lambda x: markov(order, x[:-1])),
#                   tc.pluck(ops),
#                   lambda xs: zip(*xs),
#                   tc.map(agf),
#                   list)
#   return markov_aggregator

# aggregate_markov_tables(1, ['N-N', 'N-R', 'R-R', 'R-N'], mean)(tree)

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


def leaf_height(aggregator):
  def leaf_height_wrapper(tree):
    if not isinstance(tree, list): return 0
    return aggregator(height_list(tree))
  return leaf_height_wrapper


def max_operation_depth(op):
  def ops_depth(tree):
    if not isinstance(tree, list): return 0
    if extract_op(tree[0]) == op:
      return depth(tree)
    return max( ops_depth(c) for c in tree[1:])
  return ops_depth


def inorder_pos(op, aggregator):
  def inorder_pos_wrapper(tree):
    return aggregator(x[0] for x in enumerate(in_order(tree))
                      if extract_op(x[1]) == op)

  return inorder_pos_wrapper


def markov_tables(tree):
  result = {}
  # for orders 1 and 2:
  for order in xrange(1, 3):
    keySet, averages = set(), {}
    # process the initial sliding window to just contain N/R's
    paths = [list(list(_.split('^')[0][1] if ':' in _ else _ for _ in elem)
      for elem in t.sliding_window(order, path))
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
  # these three, being basic "dimensions" of a tree, are also allowed
  # to be left alone.
  ('length', length, (lambda x: 1,)),
  ('depth', depth, (lambda x: 1, length)),

  ('num_nodes', num_nodes, (lambda x: 1, length)),
  ('num_normal', op_counter(':N'), (num_nodes,)),
  ('num_reverse', op_counter(':R'), (num_nodes,)),

  ('reverse_max_depth', max_operation_depth(':R'), (length, depth)),

  ('max_range_reverse', op_range(max, ':R'), (length,)),
  ('min_range_reverse', op_range(min, ':R'), (length,)),
  ('mean_range_reverse', op_range(mean, ':R'), (length,)),
  ('stdev_range_reverse', op_range(stdev, ':R'), (length,)),

  # max leaf height is the same as depth of tree
  ('mean_leaf_height', leaf_height(mean), (length, depth)),
  ('stdev_leaf_height', leaf_height(stdev), (length, depth)),
  ('min_leaf_height', leaf_height(min), (length, depth)),


  ('mean_inorder_pos_reverse', inorder_pos(':R', mean), (num_nodes,)),
  ('stdev_inorder_pos_reverse', inorder_pos(':R', stdev), (num_nodes,))
]

# add compressed versions of the features.
features += [('compressed_' + x[0], t.compose(x[1], compress), [t.compose(f, compress) for f in x[2]])
             for x in features]


if __name__ == '__main__':

  markov_features = ['markov_N', 'markov_R', 'markov_NR', 'markov_RN', 'markov_NN', 'markov_RR']
  opts, args = getopt.getopt(sys.argv[1:], 'l:n', ['--language', '--normalize'])
  language = None
  normalize = False
  for o,a in opts:
    if o == '-l' or o == '--language':
      language = a + ','
    if o == '-n' or o == '--normalize':
      normalize = True

  # Generate header for feature values
  print(('language,' if language is not None else '') +
          (','.join(','.join(x[0] + (lambda s: '' if s[0] == '<' else '__' + s)(nf.__name__)
                             for nf in x[2]) for x in features) if normalize
            else ','.join(x[0] for x in features)) + ',' +
          ','.join(markov_features) + ',' +
          ','.join([('compressed_' + f) for f in markov_features]))

  # For each tree, compute its associated feature values
  for line in fileinput.input(args):
    tree = parse_sexp(line)[0]
    print((language or '') + ','.join([str(','.join(str(float(f[1](tree)/float(nf(tree)))) for nf in f[2]) if normalize else f[1](tree)) for f in features] +
      list(t.get(markov_features, markov_tables(tree), str(0.0))) +
      list(t.get(markov_features, markov_tables(compress(tree)), str(0.0)))))

