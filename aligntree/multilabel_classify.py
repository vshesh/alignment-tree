from sklearn import svm, metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.mixture import GMM
from sklearn.multiclass import OneVsRestClassifier
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

all_data = np.row_stack(langs)
labels = []

for i in xrange(len(langs)):
  l = langs[i]
  expected = [sys.argv[1+i] if np.any(np.equal(l,x).all(1)) else '' for x in all_data]
  labels.append(expected)

labels = [[l for l in list(label) if len(l) > 0] for label in zip(*labels)]
mlb = MultiLabelBinarizer()
indicators = mlb.fit_transform(labels)

# clf = OneVsRestClassifier(GMM(n_components = 4, covariance_type='full'))
clf = OneVsRestClassifier(svm.SVC())
# clf = OneVsRestClassifier(SGDClassifier())
clf.fit(all_data, indicators)

pred =  clf.predict(all_data)

for i in xrange(pred.shape[1]):
  print mlb.classes_[i]

  print t.frequencies(indicators[:,i]), t.frequencies(zip(indicators[:,i],pred[:,i]))

  print metrics.classification_report(indicators[:,i], pred[:,i])

