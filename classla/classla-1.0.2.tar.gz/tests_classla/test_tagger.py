"""
Basic testing of part of speech tagging
"""

import classla

from tests_classla import *

SL_DOC = "France Prešeren se je rodil v vrbi."


SL_DOC_GOLD = """
<Token id=1;words=[<Word id=1;text=France;upos=PROPN;xpos=Npmsn;feats=Case=Nom|Gender=Masc|Number=Sing>]>
<Token id=2;words=[<Word id=2;text=Prešeren;upos=PROPN;xpos=Npmsn;feats=Case=Nom|Gender=Masc|Number=Sing>]>
<Token id=3;words=[<Word id=3;text=se;upos=PRON;xpos=Px------y;feats=PronType=Prs|Reflex=Yes|Variant=Short>]>
<Token id=4;words=[<Word id=4;text=je;upos=AUX;xpos=Va-r3s-n;feats=Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin>]>
<Token id=5;words=[<Word id=5;text=rodil;upos=VERB;xpos=Vmbp-sm;feats=Gender=Masc|Number=Sing|VerbForm=Part>]>
<Token id=6;words=[<Word id=6;text=v;upos=ADP;xpos=Sl;feats=Case=Loc>]>
<Token id=7;words=[<Word id=7;text=vrbi;upos=NOUN;xpos=Ncfsl;feats=Case=Loc|Gender=Fem|Number=Sing>]>
<Token id=8;words=[<Word id=8;text=.;upos=PUNCT;xpos=Z>]>
""".strip()


def test_part_of_speech():
    nlp = classla.Pipeline(**{'processors': 'tokenize,pos', 'dir': TEST_MODELS_DIR, 'lang': 'sl'})
    doc = nlp(SL_DOC)
    assert SL_DOC_GOLD == '\n\n'.join([sent.tokens_string() for sent in doc.sentences])
