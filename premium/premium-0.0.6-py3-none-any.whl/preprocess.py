import imp
import pickle
from typing import Any, List

import codefast as cf
import jieba
import numpy as np
from codefast.cn import strip_punc
from numpy.lib.arraypad import pad
from scipy import stats
from codefast.utils import deprecated


class Pickle:
    def read(self, pickle_file: str):
        return pickle.load(open(pickle_file, 'rb'))

    def write(self, contents, pickle_file: str):
        with open(pickle_file, 'wb') as f:
            pickle.dump(contents, f)


class Text:
    '''processing text file'''
    @staticmethod
    def strip_stopwords(X: List[str], stop_words: List = None) -> List[str]:
        if stop_words is None:
            from .config import stop_words
            _stop_words = stop_words
        else:
            _stop_words = set(stop_words)
        for i, u in enumerate(X):
            X[i] = ' '.join(
                [v for v in u.split(' ') if v not in _stop_words and v != ' '])
        return X


class Disposable:
    def normalize(self, X):
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        _ = scaler.fit_transform(X)
        return _, scaler

    def minmax(self, X):
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        _ = scaler.fit_transform(X)
        return _, scaler

    def jb_cut(self, X:List, remove_punc:bool=False)->List:
        us = [' '.join(jieba.lcut(u)) for u in X]
        if remove_punc:
            return [strip_punc(u) for u in us]
        return us


once = Disposable()

@deprecated('use once.jb_cut instead.')
def jb_cut(X) -> List[Any]:
    if isinstance(X, str):
        return strip_punc(' '.join(jieba.lcut(X)))
    return [strip_punc(' '.join(jieba.lcut(_))) for _ in X]


def any_cn(X) -> bool:
    '''Decides any Chinese char was contained'''
    if isinstance(X, str):
        X = [X]
    return any(cf.nstr(s).is_cn() for s in X)


def datainfo(sequences: list) -> None:
    len_list = list(map(len, sequences))

    def percentile(n: int):
        return int(np.percentile(len_list, n))

    print('{:<30} {}'.format('Size of sequence:', len(sequences)))
    print('{:<30} {}'.format('Maximum length:', max(len_list)))
    print('{:<30} {}'.format('Minimum length:', min(len_list)))
    print('{:<30} {}'.format('Percentile 90 :', percentile(90)))
    print('{:<30} {}'.format('Percentile 80 :', percentile(80)))
    print('{:<30} {}'.format('Percentile 20 :', percentile(20)))
    print('{:<30} {}'.format('Percentile 10 :', percentile(10)))
    print('{:<30} {}'.format('The mode is :', stats.mode(len_list)[0]))

    if any_cn(sequences):
        import jieba
        sequences = [jieba.lcut(s) for s in sequences]
    _, tokenizer = tokenize(sequences)
    print('unique words count {}'.format(len(tokenizer.word_index)))


def list_physical_devices()->list:
    from tensorflow.python.eager import context
    _devices = context.context().list_physical_devices()
    cf.info(_devices)
    return _devices

def tokenize(X: list, max_feature: int = 10000) -> list:
    cf.info(f'Tokenizing texts')
    from tensorflow.keras.preprocessing.text import Tokenizer
    tok = Tokenizer(num_words=max_feature)
    tok.fit_on_texts(X)
    ans = tok.texts_to_sequences(X)
    return ans, tok


def label_encode(y: list, return_processor: bool = False) -> np.ndarray:
    '''Encode labels into 0, 1, 2...'''
    cf.info(
        f'Getting binary labels. Return encoder is set to {return_processor}')
    from sklearn.preprocessing import LabelEncoder
    enc = LabelEncoder()
    y_categories = enc.fit_transform(y)
    return (y_categories, enc) if return_processor else y_categories


def onehot_encode(y: list, return_processor: bool = False) -> np.ndarray:
    '''input format: y =[['red'], ['green'], ['blue']]
    '''
    cf.info(
        f'Getting one hot encode labels. Return encoder is set to {return_processor}'
    )
    assert isinstance(y[0], list) or isinstance(y[0], np.ndarray)
    from sklearn.preprocessing import OneHotEncoder
    enc = OneHotEncoder()
    y_categories = enc.fit_transform(y)
    return (y_categories, enc) if return_processor else y_categories


def pad_sequences(sequences, **kwargs):
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    seq = pad_sequences(sequences, **kwargs)
    return seq


pkl = Pickle()

contraction_dict = {
    "ain't": "is not",
    "aren't": "are not",
    "can't": "cannot",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he would",
    "he'll": "he will",
    "he's": "he is",
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    "how's": "how is",
    "I'd": "I would",
    "I'd've": "I would have",
    "I'll": "I will",
    "I'll've": "I will have",
    "I'm": "I am",
    "I've": "I have",
    "i'd": "i would",
    "i'd've": "i would have",
    "i'll": "i will",
    "i'll've": "i will have",
    "i'm": "i am",
    "i've": "i have",
    "isn't": "is not",
    "it'd": "it would",
    "it'd've": "it would have",
    "it'll": "it will",
    "it'll've": "it will have",
    "it's": "it is",
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have",
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "o'clock": "of the clock",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    "she'd": "she would",
    "she'd've": "she would have",
    "she'll": "she will",
    "she'll've": "she will have",
    "she's": "she is",
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    "so's": "so as",
    "this's": "this is",
    "that'd": "that would",
    "that'd've": "that would have",
    "that's": "that is",
    "there'd": "there would",
    "there'd've": "there would have",
    "there's": "there is",
    "here's": "here is",
    "they'd": "they would",
    "they'd've": "they would have",
    "they'll": "they will",
    "they'll've": "they will have",
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    "we'd": "we would",
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what'll": "what will",
    "what'll've": "what will have",
    "what're": "what are",
    "what's": "what is",
    "what've": "what have",
    "when's": "when is",
    "when've": "when have",
    "where'd": "where did",
    "where's": "where is",
    "where've": "where have",
    "who'll": "who will",
    "who'll've": "who will have",
    "who's": "who is",
    "who've": "who have",
    "why's": "why is",
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    "you'd": "you would",
    "you'd've": "you would have",
    "you'll": "you will",
    "you'll've": "you will have",
    "you're": "you are",
    "you've": "you have"
}
