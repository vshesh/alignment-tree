from sklearn import svm, metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import Normalizer
from sklearn.mixture import GMM
import numpy as np
import toolz as t


def read_file_to_scipy_data(file_name, label):
	f = open(file_name)
	f.readline()
	data = np.loadtxt(f, delimiter=',')
	labels = [label for a in data]
	return (data, labels)

arabic = read_file_to_scipy_data('./features/arabic-english-features-small.csv', 'arabic')
german = read_file_to_scipy_data('./features/de-partial-small.output', 'german')
french = read_file_to_scipy_data('./features/fr-partial-small.output', 'french')
spanish = read_file_to_scipy_data('./features/es-partial-small.output', 'spanish')

all_data =  np.row_stack((arabic[0], german[0], french[0], spanish[0]))
all_labels = arabic[1] + german[1] + french[1] + spanish[1]

norm_data = Normalizer().fit_transform(all_data, all_labels)

# clf = GMM(n_components=4, covariance_type='full')

clf = svm.SVC()

print 'fitting'
clf.fit(all_data, all_labels)

print 'predicting on training data'
predictions = clf.predict(all_data)



print metrics.classification_report(predictions, all_labels)# map(lambda x:{'arabic':1,'german':0,'french':2,'spanish':3}[x], all_labels))

# new_clf = SGDClassifier(n_iter=300, n_jobs=-1)

# print 'fitting'
# new_clf.fit(norm_data, all_labels)

# print 'predicting on training data'
# new_pred = new_clf.predict(all_data)

# print metrics.classification_report(new_pred, all_labels)

