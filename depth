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


if __name__ == '__main__':
  for line in sys.stdin:
    print(depth(parse_sexp(line)[0]))