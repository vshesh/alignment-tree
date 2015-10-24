#!/usr/bin/env python
from __future__ import print_function

import toolz as t
import sys


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
  return '('+tree[0] + ' ' + ' '.join(dumptree(child) for child in tree[1:]) + ')'

def dumpshape(tree):
  if tree is None: return ''
  if not isinstance(tree,list): return '*'
  return '('+tree[0] + ' ' + ' '.join(dumpshape(child) for child in tree[1:]) + ')'  

def subtrees(sexp):
  if sexp is None: return
  if not isinstance(sexp, list): return
  print(dumpshape(sexp))
  for c in sexp[1:]:
    subtrees(c)


if __name__ == '__main__':
  for line in sys.stdin:
    subtrees(parse_sexp(line)[0])