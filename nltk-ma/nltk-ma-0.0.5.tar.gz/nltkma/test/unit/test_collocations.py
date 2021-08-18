from nltkma.collocations import BigramCollocationFinder
from nltkma.metrics import BigramAssocMeasures

## Test bigram counters with discontinuous bigrams and repeated words

_EPSILON = 1e-8
SENT = 'this this is is a a test test'.split()


def close_enough(x, y):
    """Verify that two sequences of n-gram association values are within
       _EPSILON of each other.
    """

    return all(abs(x1[1] - y1[1]) <= _EPSILON for x1, y1 in zip(x, y))


def test_bigram_1():
    pivot_tokens = ['numbers']
    target_tokens = ['calls', 'personal', 'numbers']
    corpus = ['calls', 'to', '0800', 'numbers', 'are', 'numbers', 'free', 'from', 'from', 'personal', 'mobiles',
              'and',
              'landlines']

    b = BigramCollocationFinder.from_words(pivot_tokens, target_tokens, corpus, (4, 4), allow_self_reference=True)

    assert sorted(b.ngram_fd.items()) == [(('calls', 'numbers'), 1), (('numbers', 'numbers'), 1),
                                          (('numbers', 'personal'), 1)]
    assert b.dist == {('calls', 'numbers'): [3], ('numbers', 'numbers'): [2], ('numbers', 'personal'): [4]}
    assert b.pos == {('calls', 'numbers'): [3], ('numbers', 'numbers'): [3], ('numbers', 'personal'): [5]}


def test_bigram_2():
    pivot_tokens = ['test']
    target_tokens = ['calls', 'personal', 'numbers']
    corpus = ['calls', 'to', '0800', 'numbers', 'are', 'numbers', 'free', 'from', 'from', 'personal', 'mobiles',
              'and',
              'landlines']

    b = BigramCollocationFinder.from_words(pivot_tokens, target_tokens, corpus, (4, 4), allow_self_reference=True)

    assert sorted(b.ngram_fd.items()) == []
    assert b.dist == {}
    assert b.pos == {}


def test_bigram_3():
    pivot_tokens = ['numbers', 'landlines']
    target_tokens = ['calls', 'personal', 'numbers']
    corpus = ['calls', 'to', '0800', 'numbers', 'are', 'numbers', 'free', 'from', 'from', 'personal', 'mobiles',
              'and',
              'landlines']

    b = BigramCollocationFinder.from_words(pivot_tokens, target_tokens, corpus, (4, 4), allow_self_reference=True)

    assert sorted(b.ngram_fd.items()) == [(('calls', 'numbers'), 1), (('numbers', 'numbers'), 1),
                                          (('numbers', 'personal'), 1), (('personal', 'landlines'), 1)]
    assert b.dist == {('calls', 'numbers'): [3], ('numbers', 'numbers'): [2], ('numbers', 'personal'): [4],
                      ('personal', 'landlines'): [3]}
    assert b.pos == {('calls', 'numbers'): [3], ('numbers', 'numbers'): [3], ('numbers', 'personal'): [5],
                     ('personal', 'landlines'): [12]}


def test_bigram_4():
    pivot_tokens = ['numbers', 'landlines']
    target_tokens = ['calls', 'personal', 'numbers']
    corpus = ['calls', 'to', '0800', 'numbers', 'are', 'numbers', 'free', 'from', 'from', 'personal', 'mobiles',
              'personal', 'and', 'landlines']

    b = BigramCollocationFinder.from_words(pivot_tokens, target_tokens, corpus, (4, 4), allow_self_reference=True)

    assert sorted(b.ngram_fd.items()) == [(('calls', 'numbers'), 1), (('numbers', 'numbers'), 1),
                                          (('numbers', 'personal'), 1), (('personal', 'landlines'), 2)]
    assert b.dist == {('calls', 'numbers'): [3], ('numbers', 'numbers'): [2], ('numbers', 'personal'): [4],
                      ('personal', 'landlines'): [4, 2]}
    assert b.pos == {('calls', 'numbers'): [3], ('numbers', 'numbers'): [3], ('numbers', 'personal'): [5],
                     ('personal', 'landlines'): [13, 13]}

def test_bigram_5():
    pivot_tokens = ['numbers', 'landlines']
    target_tokens = ['calls', 'personal', 'numbers']
    corpus = ['calls', 'to', '0800', 'numbers', 'are', 'numbers', 'free', 'from', 'from', 'personal', 'mobiles',
              'personal', 'and', 'landlines']

    b = BigramCollocationFinder.from_words(pivot_tokens, target_tokens, corpus, (2, 2), allow_self_reference=True)
    score =  b.score_ngrams(BigramAssocMeasures.pmi)

    assert sorted(b.ngram_fd.items()) == [(('numbers', 'numbers'), 1),
                                           (('personal', 'landlines'), 1)]
    assert b.dist == {('numbers', 'numbers'): [2],
                      ('personal', 'landlines'): [2]}
    assert b.pos == {('numbers', 'numbers'): [3],
                     ('personal', 'landlines'): [13]}

def test_bigram_6():
    pivot_tokens = ['numbers', 'landlines']
    target_tokens = ['calls', 'personal', 'numbers']
    corpus = ['calls', 'to', '0800', 'numbers', 'are', 'numbers', 'free', 'from', 'from', 'personal', 'mobiles',
              'personal', 'and', 'landlines']

    b = BigramCollocationFinder.from_words(pivot_tokens, target_tokens, corpus, (2, 2), allow_self_reference=False)

    assert sorted(b.ngram_fd.items()) == [(('personal', 'landlines'), 1)]
    assert b.dist == {('personal', 'landlines'): [2]}
    assert b.pos == {('personal', 'landlines'): [13]}

    assert close_enough(
        sorted(b.score_ngrams(BigramAssocMeasures.pmi)),
        sorted([(('personal', 'landlines'), 0.5849625007211561)]))

def test_bigram_7():
    corpus_token = ['Traditionally', ',', 'black', 'Black', 'Asians', 'Blacks', 'blacks', 'bame', 'a', 'text', 'is',
                    'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'understood', 'minority',
                    ',', 'asian', 'to', 'be', 'a', ',' 'piece', 'of', 'written', 'or', 'spoken', 'material', '.',
                    'in', 'its', 'primary', 'form', '(', 'as', 'opposed', 'to', 'a', 'paraphrase', 'or']
    corpus_token_cleaned = ['Traditionally', 'black', 'Black', 'Asians', 'Blacks', 'blacks', 'bame', 'a', 'text',
                            'is',
                            'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'BAME', 'Asian', 'understood',
                            'minority',
                            'asian', 'to', 'be', 'a', 'piece', 'of', 'written', 'or', 'spoken', 'material', 'in',
                            'its',
                            'primary', 'form', '(', 'as', 'opposed', 'to', 'a', 'paraphrase', 'or']

    pivot_token = ['minority']
    target_token = ['asian']

    b = BigramCollocationFinder.from_words(pivot_token,target_token,corpus_token_cleaned,(3,3),True)
