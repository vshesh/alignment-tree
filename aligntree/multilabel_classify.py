from sklearn import svm, metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.mixture import GMM
from sklearn.multiclass import OneVsRestClassifier
from sklearn.cross_validation import train_test_split
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

train, test, y_train, y_test = train_test_split(all_data, indicators)

# clf = OneVsRestClassifier(GMM(n_components = 4, covariance_type='full'))
clf = OneVsRestClassifier(svm.SVC())
# clf = OneVsRestClassifier(SGDClassifier())
clf.fit(train, y_train)

train_pred =  clf.predict(train)
test_pred = clf.predict(test)

for i in xrange(train_pred.shape[1]):
  print mlb.classes_[i]
  print "Train data"
  print t.frequencies(y_train[:,i]), t.frequencies(zip(y_train[:,i],train_pred[:,i]))
  print metrics.classification_report(y_train[:,i], train_pred[:,i])
  print "Test data"
  print t.frequencies(y_test[:,i]), t.frequencies(zip(y_test[:,i],test_pred[:,i]))
  print metrics.classification_report(y_test[:,i], test_pred[:,i])
  print ""

#test_set = ["features/de-test-10000.features", "features/fr-test-10000.features"]