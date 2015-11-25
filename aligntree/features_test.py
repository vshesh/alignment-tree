from __future__ import print_function

import toolz as t
import aligntree.features as f


smalltree = f.parse_sexp('(:N^0-2 (:N^0-1 0 1) 2)')[0]
smallishtree = f.parse_sexp('(:N^0-13 (:N^0-12 (:N^0-11 (:N^0-10 (:N^0-9 (:N^0-8 (:N^0-7 (:N^0-6 (:N^0-5 (:N^0-4 (:N^0-3 (:N^0-2 (:N^0-1 0 1) 2) 3) 4) 5) 6) 7) 8) 9) 10) 11) 12) 13)')[0]
mediumtree = f.parse_sexp('(:N^0-21 (:R^0-20 (:R^3-20 (:R^4-20 (:R^5-20 (:R^8-20 (:N^9-20 (:N^9-19 (:N^9-18 (:N^9-17 (:N^9-11 (:N^9-10 9 10) 11) (:R^12-17 (:R^14-17 (:N^15-17 (:N^15-16 15 16) 17) 14) (:N^12-13 12 13))) 18) 19) 20) 8) (:N^5-7 (:N^5-6 5 6) 7)) 4) 3) (:N^0-2 (:N^0-1 0 1) 2)) 21)')[0]


def test_length():
  assert(f.length(smalltree) == 2)
  assert(f.length(mediumtree) == 21)

  assert(f.length(smalltree) == f.length(f.compress(smalltree)))
  assert(f.length(mediumtree) == f.length(f.compress(mediumtree)))


def test_num_nodes():
  assert(f.num_nodes(smalltree) == 2)
  assert(f.num_nodes(mediumtree) == 21)

  assert(f.num_nodes(smalltree) == f.length(smalltree))
  assert(f.num_nodes(mediumtree) == f.length(mediumtree))


def test_depth():
  assert(f.depth(smalltree) == 2)
  assert(f.depth(mediumtree) == 14)


def test_op_count():
  normalops = f.op_counter(':N')
  reverseops = f.op_counter(':R')

  assert(normalops(smalltree) == 2)
  assert(reverseops(smalltree) == 0)
  assert(normalops(smalltree) + reverseops(smalltree) == f.num_nodes(smalltree))

  assert(normalops(mediumtree) == 14)
  assert(reverseops(mediumtree) == 7)
  assert(normalops(mediumtree) + reverseops(mediumtree) == f.num_nodes(mediumtree))


def test_in_order_traversal():
  assert(f.mean_x_pos_R_in_tree(smalltree) == 0)
  assert(int(f.mean_x_pos_R_in_tree(mediumtree)) == 24)
