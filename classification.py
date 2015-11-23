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

arabic = read_file_to_scipy_data('./features/arabic-english-features.csv', 'arabic')
german = read_file_to_scipy_data('./features/de-partial.output', 'german')
french = read_file_to_scipy_data('./features/fr-partial.output', 'french')
spanish = read_file_to_scipy_data('./features/es-partial.output', 'spanish')

all_data =  np.row_stack((arabic[0], german[0], french[0], spanish[0]))
all_labels = arabic[1] + german[1] + french[1] + spanish[1]



norm_data = Normalizer().fit_transform(all_data, all_labels)

# clf = GMM(n_components=4, covariance_type='full')
arabic_clf = GMM(n_components=4, covariance_type='full')
german_clf = GMM(n_components=4, covariance_type='full')
french_clf = GMM(n_components=4, covariance_type='full')
spanish_clf = GMM(n_components=4, covariance_type='full')

arabic_clf.fit(arabic[0])
german_clf.fit(german[0])
french_clf.fit(french[0])
spanish_clf.fit(spanish[0])

arabic_predictions = arabic_clf.predict(all_data)
german_predictions = german_clf.predict(all_data)
french_predictions = french_clf.predict(all_data)
spanish_predictions = spanish_clf.predict(all_data)

prediction_probs = zip(arabic_predictions, german_predictions, french_predictions, spanish_predictions)
predictions = [max(enumerate(p), key=lambda x: x[1])[0] for p in prediction_probs]

predition_labels = map(lambda x:{0:'arabic', 1:'german', 2:'french', 3:'spanish'}[x], predictions)


print metrics.classification_report(predition_labels, all_labels)# map(lambda x:{'arabic':1,'german':0,'french':2,'spanish':3}[x], all_labels))

# new_clf = SGDClassifier(n_iter=300, n_jobs=-1)

# print 'fitting'
# new_clf.fit(norm_data, all_labels)

# print 'predicting on training data'
# new_pred = new_clf.predict(all_data)

# print metrics.classification_report(new_pred, all_labels)

