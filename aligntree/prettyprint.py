#!/usr/bin/env python
from __future__ import print_function

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


def prettyprint(sexp, spaces=1):
  if sexp is None: return ''
  if not isinstance(sexp, list): return str(sexp)
  if all(not isinstance(x, list) for x in sexp):
    return '(' + ' '.join(map(str, sexp)) + ')'

  stringify = lambda x: ' '*spaces + prettyprint(x, spaces).replace('\n', '\n'+' '*spaces)
  s = '(' + sexp[0] + '\n'
  if len(sexp) > 2:
    s += '\n'.join(map(stringify, sexp[1:-1])) + '\n'
  s += stringify(sexp[-1]) + ')'
  return s


if __name__ == '__main__':
  for line in sys.stdin:
    print(prettyprint(parse_sexp(line)[0]))