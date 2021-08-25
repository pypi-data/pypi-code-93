"""
Basic testing of lemmatization
"""

import classla
from classla.utils.conll import CoNLL

from tests_classla import *

SL_DOC = "France Prešeren se je rodil v vrbi."

SL_DOC_IDENTITY_GOLD = """
<Token id=1;words=[<Word id=1;text=France;lemma=France>]>
<Token id=2;words=[<Word id=2;text=Prešeren;lemma=Prešeren>]>
<Token id=3;words=[<Word id=3;text=se;lemma=se>]>
<Token id=4;words=[<Word id=4;text=je;lemma=je>]>
<Token id=5;words=[<Word id=5;text=rodil;lemma=rodil>]>
<Token id=6;words=[<Word id=6;text=v;lemma=v>]>
<Token id=7;words=[<Word id=7;text=vrbi;lemma=vrbi>]>
<Token id=8;words=[<Word id=8;text=.;lemma=.>]>
""".strip()

SL_DOC_LEMMATIZER_MODEL_GOLD = """
<Token id=1;words=[<Word id=1;text=France;lemma=France;upos=PROPN;xpos=Npmsn;feats=Case=Nom|Gender=Masc|Number=Sing>]>
<Token id=2;words=[<Word id=2;text=Prešeren;lemma=Prešeren;upos=PROPN;xpos=Npmsn;feats=Case=Nom|Gender=Masc|Number=Sing>]>
<Token id=3;words=[<Word id=3;text=se;lemma=se;upos=PRON;xpos=Px------y;feats=PronType=Prs|Reflex=Yes|Variant=Short>]>
<Token id=4;words=[<Word id=4;text=je;lemma=biti;upos=AUX;xpos=Va-r3s-n;feats=Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin>]>
<Token id=5;words=[<Word id=5;text=rodil;lemma=roditi;upos=VERB;xpos=Vmbp-sm;feats=Gender=Masc|Number=Sing|VerbForm=Part>]>
<Token id=6;words=[<Word id=6;text=v;lemma=v;upos=ADP;xpos=Sl;feats=Case=Loc>]>
<Token id=7;words=[<Word id=7;text=vrbi;lemma=vrba;upos=NOUN;xpos=Ncfsl;feats=Case=Loc|Gender=Fem|Number=Sing>]>
<Token id=8;words=[<Word id=8;text=.;lemma=.;upos=PUNCT;xpos=Z>]>
""".strip()


def test_identity_lemmatizer():
    nlp = classla.Pipeline(**{'processors': 'tokenize,lemma', 'dir': TEST_MODELS_DIR, 'lang': 'sl',
                                  'lemma_use_identity': True})
    doc = nlp(SL_DOC)
    assert SL_DOC_IDENTITY_GOLD == '\n\n'.join([sent.tokens_string() for sent in doc.sentences])


def test_full_lemmatizer():
    nlp = classla.Pipeline(**{'processors': 'tokenize,pos,lemma', 'dir': TEST_MODELS_DIR, 'lang': 'sl'})
    doc = nlp(SL_DOC)
    assert SL_DOC_LEMMATIZER_MODEL_GOLD == '\n\n'.join([sent.tokens_string() for sent in doc.sentences])
