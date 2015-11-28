from sklearn import svm, metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import Normalizer
from sklearn.mixture import GMM
import math
import numpy as np
import toolz as t
import os
import csv
import sys

if len(sys.argv) < 3:
  print 'Must have at least two filenames'
  exit(1)

langs = []
for filename in sys.argv[1:]:
  with open(filename, 'rb') as f:
    langs.append(np.loadtxt(f, delimiter=',', skiprows=1))

gmms = []
for l in langs:
  g = GMM(n_components = 2, covariance_type='full')
  g.fit(l)
  gmms.append(g)

all_data = np.row_stack(langs)
print len(all_data)
for i in xrange(len(gmms)):
  g = gmms[i]
  l = langs[i]
  print len(l)
  pred = [x > math.log(0.5) for x in g.score(all_data)]
  expected = [~np.all(l-x) for x in all_data]
  print pred
  print expected

