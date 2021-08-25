"""
Basic testing of part of speech tagging
"""

import classla
from classla.utils.conll import CoNLL

from tests_classla import *

SL_DOC = "France Prešeren se je rodil v Vrbi."


SL_DOC_GOLD = """
# newpar id = 1
# sent_id = 1.1
# text = France Prešeren se je rodil v Vrbi.
1	France	_	_	_	_	_	_	_	NER=B-PER
2	Prešeren	_	_	_	_	_	_	_	NER=I-PER
3	se	_	_	_	_	_	_	_	NER=O
4	je	_	_	_	_	_	_	_	NER=O
5	rodil	_	_	_	_	_	_	_	NER=O
6	v	_	_	_	_	_	_	_	NER=O
7	Vrbi	_	_	_	_	_	_	_	NER=B-LOC|SpaceAfter=No
8	.	_	_	_	_	_	_	_	NER=O

""".lstrip()


def test_ner():
    nlp = classla.Pipeline(**{'processors': 'tokenize,ner', 'dir': TEST_MODELS_DIR, 'lang': 'sl'})
    doc = nlp(SL_DOC)
    assert SL_DOC_GOLD == doc.to_conll()
