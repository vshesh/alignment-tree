from sklearn import svm, metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import Normalizer
from sklearn.mixture import GMM
import math
import numpy as np
import toolz as t


def read_file_to_scipy_data(file_name, label):
	f = open(file_name)
	f.readline()
	data = np.loadtxt(f, delimiter=',')
	labels = [label for a in data]
	return (data, labels)

arabic = read_file_to_scipy_data('./features/arabic.features', 'arabic')
german = read_file_to_scipy_data('./features/de.features', 'german')
french = read_file_to_scipy_data('./features/fr.features', 'french')

all_data =  np.row_stack((arabic[0], german[0], french[0]))
all_labels = arabic[1], german[1] + french[1]
norm_data = Normalizer().fit_transform(all_data, all_labels)

arabic_clf = GMM(n_components=4, covariance_type='full')
german_clf = GMM(n_components=4, covariance_type='full')
french_clf = GMM(n_components=4, covariance_type='full')

arabic_clf.fit(arabic[0])
german_clf.fit(german[0])
french_clf.fit(french[0])

arabic_predictions = arabic_clf.score(all_data)
german_predictions = german_clf.score(all_data)
french_predictions = french_clf.score(all_data)

# prediction_probs = zip(arabic_predictions, german_predictions, french_predictions)
# predictions = [max(enumerate(p), key=lambda x: x[1])[0] for p in prediction_probs]

# predition_labels = map(lambda x:{0:'arabic', 1:'german', 2:'french'}[x], predictions)

#lets just do german

true_labels = [1 if x in german[0] else 0 for x in all_data]
print german_predictions
predictions = [1 if x >= 0 else 0 for x in german_predictions]


print "GMM"
print metrics.classification_report(predictions, true_labels)# map(lambda x:{'arabic':1,'german':0,'french':2,'spanish':3}[x], all_labels))
