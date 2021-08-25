"""
Basic testing of dependency parser
"""

import classla
from classla.utils.conll import CoNLL

from tests_classla import *


SL_DOC = "France Prešeren se je rodil v Vrbi."

SL_DOC_GOLD = """
# newpar id = 1
# sent_id = 1.1
# text = France Prešeren se je rodil v Vrbi.
1	France	France	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	5	nsubj	_	_
2	Prešeren	Prešeren	PROPN	Npmsn	Case=Nom|Gender=Masc|Number=Sing	1	flat:name	_	_
3	se	se	PRON	Px------y	PronType=Prs|Reflex=Yes|Variant=Short	5	expl	_	_
4	je	biti	AUX	Va-r3s-n	Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin	5	aux	_	_
5	rodil	roditi	VERB	Vmbp-sm	Gender=Masc|Number=Sing|VerbForm=Part	0	root	_	_
6	v	v	ADP	Sl	Case=Loc	7	case	_	_
7	Vrbi	Vrba	PROPN	Npfsl	Case=Loc|Gender=Fem|Number=Sing	5	obl	_	SpaceAfter=No
8	.	.	PUNCT	Z	_	5	punct	_	_

""".lstrip()


def test_parser():
    nlp = classla.Pipeline(
        **{'processors': 'tokenize,pos,lemma,depparse', 'dir': TEST_MODELS_DIR, 'lang': 'sl'})
    doc = nlp(SL_DOC)
    assert SL_DOC_GOLD == doc.to_conll()
