from bottle import Bottle, route, run, static_file, template
from bottle import request, response, abort, error, HTTPResponse
import cPickle

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
from aligntree.features import featurize
from aligntree.treegeneration import treegeneration

app = Bottle()

@app.route('/hello')
def hello():
    
    return "Hello World!\n"

clf = cPickle.load(open('trained_classifier_swed,arab,fren,deut-all.pkl','r'))
lang_to_num = {'arabic': 0, 'german': 1, 'french': 2, 'swedish': 3}

@app.route('/classifier/<language>/<query>') # classifier/arabic/0-1 0-1 3-4 3-5
def executeClassification(language, query):
    features = np.fromstring(featurize(treegeneration(query)), sep=',')
    prediction = clf.predict([features])
    return str(prediction[0][lang_to_num[language]])

# @route('/forum')
# def display_forum():
#    forum_id = request.query.id
#    page = request.query.page or '1'
#    return template('Forum ID: {{id}} (page {{page}})', id=forum_id, page=page)

run(app, host='localhost', port=2211)