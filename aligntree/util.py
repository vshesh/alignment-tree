#!/usr/bin/env python
import sys
import features
import getopt

# Implement util.py that enables individual running of comands like flatten, depth, etc.
# look to features.py for inspiration on how to do commandline arguments

to_flatten = False

if __name__ == '__main__':
  opts, args = getopt.getopt(sys.argv[1:], 'fdln', ['--flatten', '--depth', '-length', '--num-nodes'])
  operation = None
  for o,a in opts:
    if o == '-f' or o == '--flatten':
      to_flatten = True
    if o == '-d' or o == '--depth':
      operation = features.depth
    elif o == '-l' or o == '-length':
      operation = features.length
    elif o == '-n' or o == '--num-nodes':
      operation = features.num_nodes

  for line in sys.stdin:
    if operation != None:
      if to_flatten:
        print features.dumptree(operation(features.flatten(features.parse_sexp(line)[0])))
      else:
        print features.dumptree(operation(features.parse_sexp(line)[0]))
    else:
      if to_flatten: 
        print features.dumptree(features.flatten(features.parse_sexp(line)[0]))
