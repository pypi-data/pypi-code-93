# https://lvngd.com/blog/spacy-word-vectors-as-features-in-scikit-learn/

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np
import mysql.connector
import spacy

nlp = spacy.load("en_core_web_lg")

tknz = 'spacy'
target = 'label'
predictor = 'feedback'
db = mysql.connector.connect(option_files="my.conf", use_pure=True)
with db.cursor() as cursor:
    cursor.execute(
        "SELECT  " + target + ", " + predictor + " FROM text_data"
    )
    text_data = cursor.fetchall()
    text_data = pd.DataFrame(text_data)
    text_data.columns = cursor.column_names

text_data = text_data.rename(columns={target: "target", predictor: "predictor"})
text_data = text_data.loc[text_data.target.notnull()].copy()

# data_list = [nlp(doc).vector.reshape(1,-1) for doc in text_data.predictor]
# data = np.concatenate(data_list)


class WordVectorTransformer(TransformerMixin, BaseEstimator):
    def __init__(self, model="en_core_web_lg"):
        self.model = model

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        nlp = spacy.load(self.model)
        return np.concatenate([nlp(doc).vector.reshape(1, -1) for doc in X])


text_clf = Pipeline([
            ('vect', WordVectorTransformer()),
            ('clf', SGDClassifier(loss='log')),
            ])

text_clf.fit(text_data.predictor, text_data.target)

text_clf.score(text_data.target, text_data.target)