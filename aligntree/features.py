#!/usr/bin/env python
from __future__ import print_function

import sys
import toolz as t

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
    return list(t.cons(sexp[0], t.concat(x[1:] if isinstance(x,list) else [x] for x in children)))

  return [sexp[0]]+children


def depth(tree):
  if tree == None: return 0
  if not isinstance(tree, list): return 0
  return 1 + max(depth(x) for x in tree[1:])


def dumptree(tree):
    if (tree == None): return ''
    if not isinstance(tree, list): return str(tree)
    return '('+tree[0] + ' ' + ' '.join(dumptree(child) for child in tree[1:]) + ')'


features = [depth]

if __name__ == '__main__':
  print(','.join(f.__name__ for f in features))
  for line in sys.stdin:
    tree = parse_sexp(line)[0]
    print(','.join(str(f(tree)) for f in features))