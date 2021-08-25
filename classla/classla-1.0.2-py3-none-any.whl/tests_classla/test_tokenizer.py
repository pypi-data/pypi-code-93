"""
Basic testing of tokenization
"""

import classla

from tests_classla import *


SL_DOC = "France Prešeren je bil rojen v Vrbi. Danes je poznan kot največji slovenski pesnik. Študiral je na Dunaju."

SL_DOC_GOLD_TOKENS = """
<Token id=1;words=[<Word id=1;text=France>]>
<Token id=2;words=[<Word id=2;text=Prešeren>]>
<Token id=3;words=[<Word id=3;text=je>]>
<Token id=4;words=[<Word id=4;text=bil>]>
<Token id=5;words=[<Word id=5;text=rojen>]>
<Token id=6;words=[<Word id=6;text=v>]>
<Token id=7;words=[<Word id=7;text=Vrbi>]>
<Token id=8;words=[<Word id=8;text=.>]>

<Token id=1;words=[<Word id=1;text=Danes>]>
<Token id=2;words=[<Word id=2;text=je>]>
<Token id=3;words=[<Word id=3;text=poznan>]>
<Token id=4;words=[<Word id=4;text=kot>]>
<Token id=5;words=[<Word id=5;text=največji>]>
<Token id=6;words=[<Word id=6;text=slovenski>]>
<Token id=7;words=[<Word id=7;text=pesnik>]>
<Token id=8;words=[<Word id=8;text=.>]>

<Token id=1;words=[<Word id=1;text=Študiral>]>
<Token id=2;words=[<Word id=2;text=je>]>
<Token id=3;words=[<Word id=3;text=na>]>
<Token id=4;words=[<Word id=4;text=Dunaju>]>
<Token id=5;words=[<Word id=5;text=.>]>
""".strip()


SL_DOC_PRETOKENIZED = \
    "France Prešeren je bil rojen v Vrbi .\nDanes je poznan kot največji slovenski pesnik .\n\nŠtudiral je na Dunaju.\n"

SL_DOC_PRETOKENIZED_GOLD_TOKENS = """
<Token id=1;words=[<Word id=1;text=France>]>
<Token id=2;words=[<Word id=2;text=Prešeren>]>
<Token id=3;words=[<Word id=3;text=je>]>
<Token id=4;words=[<Word id=4;text=bil>]>
<Token id=5;words=[<Word id=5;text=rojen>]>
<Token id=6;words=[<Word id=6;text=v>]>
<Token id=7;words=[<Word id=7;text=Vrbi>]>
<Token id=8;words=[<Word id=8;text=.>]>

<Token id=1;words=[<Word id=1;text=Danes>]>
<Token id=2;words=[<Word id=2;text=je>]>
<Token id=3;words=[<Word id=3;text=poznan>]>
<Token id=4;words=[<Word id=4;text=kot>]>
<Token id=5;words=[<Word id=5;text=največji>]>
<Token id=6;words=[<Word id=6;text=slovenski>]>
<Token id=7;words=[<Word id=7;text=pesnik>]>
<Token id=8;words=[<Word id=8;text=.>]>

<Token id=1;words=[<Word id=1;text=Študiral>]>
<Token id=2;words=[<Word id=2;text=je>]>
<Token id=3;words=[<Word id=3;text=na>]>
<Token id=4;words=[<Word id=4;text=Dunaju.>]>
""".strip()


SL_DOC_PRETOKENIZED_LIST = [['France', 'Prešeren', 'je', 'bil', 'rojen', 'v', 'Vrbi', '.'], ['Danes', 'živi', 'v',
                                                                                             'poeziji', '.']]

SL_DOC_PRETOKENIZED_LIST_GOLD_TOKENS = """
<Token id=1;words=[<Word id=1;text=France>]>
<Token id=2;words=[<Word id=2;text=Prešeren>]>
<Token id=3;words=[<Word id=3;text=je>]>
<Token id=4;words=[<Word id=4;text=bil>]>
<Token id=5;words=[<Word id=5;text=rojen>]>
<Token id=6;words=[<Word id=6;text=v>]>
<Token id=7;words=[<Word id=7;text=Vrbi>]>
<Token id=8;words=[<Word id=8;text=.>]>

<Token id=1;words=[<Word id=1;text=Danes>]>
<Token id=2;words=[<Word id=2;text=živi>]>
<Token id=3;words=[<Word id=3;text=v>]>
<Token id=4;words=[<Word id=4;text=poeziji>]>
<Token id=5;words=[<Word id=5;text=.>]>
""".strip()


def test_tokenize():
    nlp = classla.Pipeline(processors='tokenize', dir=TEST_MODELS_DIR, lang='sl')
    doc = nlp(SL_DOC)
    assert SL_DOC_GOLD_TOKENS == '\n\n'.join([sent.tokens_string() for sent in doc.sentences])


def test_pretokenized():
    nlp = classla.Pipeline(**{'processors': 'tokenize', 'dir': TEST_MODELS_DIR, 'lang': 'sl',
                                  'tokenize_pretokenized': True})
    doc = nlp(SL_DOC_PRETOKENIZED)
    assert SL_DOC_PRETOKENIZED_GOLD_TOKENS == '\n\n'.join([sent.tokens_string() for sent in doc.sentences])
    doc = nlp(SL_DOC_PRETOKENIZED_LIST)
    assert SL_DOC_PRETOKENIZED_LIST_GOLD_TOKENS == '\n\n'.join([sent.tokens_string() for sent in doc.sentences])
