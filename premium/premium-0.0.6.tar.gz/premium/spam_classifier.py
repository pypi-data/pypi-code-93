#!/usr/bin/env python
import codefast as cf
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from tensorflow.keras.layers import LSTM, Dense, Dropout, Embedding
from tensorflow.keras.models import Sequential

from .measure import metrics


def get_data():
    dataset = '/tmp/spam-ham.txt'
    if not io.exists(dataset):
        from xiu.datasets import load_spam
        load_spam()
    con = io.read(dataset)
    X, y = [], []
    for c in con:
        label, text = c.split('\t')
        X.append(text)
        y.append(label)

    y = [1 if e == 'spam' else 0 for e in y]
    return X, y


def naive_bayes():
    X, y = get_data()
    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        random_state=0,
                                                        test_size=0.2)

    cv = CountVectorizer()
    X_train = cv.fit_transform(X_train)
    X_test = cv.transform(X_test)
    from premium.models.bayes import touchstone
    touchstone(X_train, y_train, X_test, y_test)


def lstm():
    from premium.keras.preprocess import label_encode, tokenize
    from premium.keras.postprocess import get_binary_prediction
    X, y = get_data()
    X, tokenizer = tokenize(X, return_processor=True)
    y = label_encode(y)
    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        y,
                                                        random_state=0,
                                                        test_size=0.2)

    max_length_sequence = max([len(e) for e in X_train])
    cf.info('max length sequence', max_length_sequence)
    cf.info('lenght of train sequences', len(X_train))
    from premium.keras.preprocess import pad_sequences
    X_train = pad_sequences(X_train, maxlen=max_length_sequence, padding="pre")
    X_test = pad_sequences(X_test, maxlen=max_length_sequence, padding="pre")

    input_dim = len(tokenizer.word_index) + 1
    from premium.models.nn import lstm_touchstone
    lstm_touchstone(X_train, y_train, X_test, y_test, input_dim)


# naive_bayes()
lstm()
# load_spam()

X = [
    'Go until jurong point, crazy.. Available only in bugis n great world la e buffet... Cine there got amore wat...',
    "Free entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005. Text FA to 87121 to receive entry question(std txt rate)T&C's apply 08452810075over18's"
]
from tensorflow.keras.preprocessing.text import Tokenizer
tok = Tokenizer()
X = ['你 好 啊！', '我 很 好']
tok.fit_on_texts(X)
XX = tok.texts_to_sequences(X + ['you never know'])
print(tok.word_index)
print(XX)
