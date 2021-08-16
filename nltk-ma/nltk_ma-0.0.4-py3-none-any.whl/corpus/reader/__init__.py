# Natural Language Toolkit: Corpus Readers
#
# Copyright (C) 2001-2021 NLTK Project
# Author: Steven Bird <stevenbird1@gmail.com>
#         Edward Loper <edloper@gmail.com>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

"""
NLTK corpus readers.  The modules in this package provide functions
that can be used to read corpus fileids in a variety of formats.  These
functions can be used to read both the corpus fileids that are
distributed in the NLTK corpus package, and corpus fileids that are part
of external corpora.

Corpus Reader Functions
=======================
Each corpus module defines one or more "corpus reader functions",
which can be used to read documents from that corpus.  These functions
take an argument, ``item``, which is used to indicate which document
should be read from the corpus:

- If ``item`` is one of the unique identifiers listed in the corpus
  module's ``items`` variable, then the corresponding document will
  be loaded from the NLTK corpus package.
- If ``item`` is a fileid, then that file will be read.

Additionally, corpus reader functions can be given lists of item
names; in which case, they will return a concatenation of the
corresponding documents.

Corpus reader functions are named based on the type of information
they return.  Some common examples, and their return types, are:

- words(): list of str
- sents(): list of (list of str)
- paras(): list of (list of (list of str))
- tagged_words(): list of (str,str) tuple
- tagged_sents(): list of (list of (str,str))
- tagged_paras(): list of (list of (list of (str,str)))
- chunked_sents(): list of (Tree w/ (str,str) leaves)
- parsed_sents(): list of (Tree with str leaves)
- parsed_paras(): list of (list of (Tree with str leaves))
- xml(): A single xml ElementTree
- raw(): unprocessed corpus contents

For example, to read a list of the words in the Brown Corpus, use
``nltk.corpus.brown.words()``:

    >>> from nltkma.corpus import brown
    >>> print(", ".join(brown.words()))
    The, Fulton, County, Grand, Jury, said, ...

"""

from nltkma.corpus.reader.plaintext import *
from nltkma.corpus.reader.util import *
from nltkma.corpus.reader.api import *
from nltkma.corpus.reader.tagged import *
from nltkma.corpus.reader.cmudict import *
from nltkma.corpus.reader.conll import *
from nltkma.corpus.reader.chunked import *
from nltkma.corpus.reader.wordlist import *
from nltkma.corpus.reader.xmldocs import *
from nltkma.corpus.reader.ppattach import *
from nltkma.corpus.reader.senseval import *
from nltkma.corpus.reader.ieer import *
from nltkma.corpus.reader.sinica_treebank import *
from nltkma.corpus.reader.bracket_parse import *
from nltkma.corpus.reader.indian import *
from nltkma.corpus.reader.toolbox import *
from nltkma.corpus.reader.timit import *
from nltkma.corpus.reader.ycoe import *
from nltkma.corpus.reader.rte import *
from nltkma.corpus.reader.string_category import *
from nltkma.corpus.reader.propbank import *
from nltkma.corpus.reader.verbnet import *
from nltkma.corpus.reader.bnc import *
from nltkma.corpus.reader.nps_chat import *
from nltkma.corpus.reader.wordnet import *
from nltkma.corpus.reader.switchboard import *
from nltkma.corpus.reader.dependency import *
from nltkma.corpus.reader.nombank import *
from nltkma.corpus.reader.ipipan import *
from nltkma.corpus.reader.pl196x import *
from nltkma.corpus.reader.knbc import *
from nltkma.corpus.reader.chasen import *
from nltkma.corpus.reader.childes import *
from nltkma.corpus.reader.aligned import *
from nltkma.corpus.reader.lin import *
from nltkma.corpus.reader.semcor import *
from nltkma.corpus.reader.framenet import *
from nltkma.corpus.reader.udhr import *
from nltkma.corpus.reader.bnc import *
from nltkma.corpus.reader.sentiwordnet import *
from nltkma.corpus.reader.twitter import *
from nltkma.corpus.reader.nkjp import *
from nltkma.corpus.reader.crubadan import *
from nltkma.corpus.reader.mte import *
from nltkma.corpus.reader.reviews import *
from nltkma.corpus.reader.opinion_lexicon import *
from nltkma.corpus.reader.pros_cons import *
from nltkma.corpus.reader.categorized_sents import *
from nltkma.corpus.reader.comparative_sents import *
from nltkma.corpus.reader.panlex_lite import *
from nltkma.corpus.reader.panlex_swadesh import *

# Make sure that nltk.corpus.reader.bracket_parse gives the module, not
# the function bracket_parse() defined in nltk.tree:
from nltkma.corpus.reader import bracket_parse

__all__ = [
    'CorpusReader',
    'CategorizedCorpusReader',
    'PlaintextCorpusReader',
    'find_corpus_fileids',
    'TaggedCorpusReader',
    'CMUDictCorpusReader',
    'ConllChunkCorpusReader',
    'WordListCorpusReader',
    'PPAttachmentCorpusReader',
    'SensevalCorpusReader',
    'IEERCorpusReader',
    'ChunkedCorpusReader',
    'SinicaTreebankCorpusReader',
    'BracketParseCorpusReader',
    'IndianCorpusReader',
    'ToolboxCorpusReader',
    'TimitCorpusReader',
    'YCOECorpusReader',
    'MacMorphoCorpusReader',
    'SyntaxCorpusReader',
    'AlpinoCorpusReader',
    'RTECorpusReader',
    'StringCategoryCorpusReader',
    'EuroparlCorpusReader',
    'CategorizedBracketParseCorpusReader',
    'CategorizedTaggedCorpusReader',
    'CategorizedPlaintextCorpusReader',
    'PortugueseCategorizedPlaintextCorpusReader',
    'tagged_treebank_para_block_reader',
    'PropbankCorpusReader',
    'VerbnetCorpusReader',
    'BNCCorpusReader',
    'ConllCorpusReader',
    'XMLCorpusReader',
    'NPSChatCorpusReader',
    'SwadeshCorpusReader',
    'WordNetCorpusReader',
    'WordNetICCorpusReader',
    'SwitchboardCorpusReader',
    'DependencyCorpusReader',
    'NombankCorpusReader',
    'IPIPANCorpusReader',
    'Pl196xCorpusReader',
    'TEICorpusView',
    'KNBCorpusReader',
    'ChasenCorpusReader',
    'CHILDESCorpusReader',
    'AlignedCorpusReader',
    'TimitTaggedCorpusReader',
    'LinThesaurusCorpusReader',
    'SemcorCorpusReader',
    'FramenetCorpusReader',
    'UdhrCorpusReader',
    'BNCCorpusReader',
    'SentiWordNetCorpusReader',
    'SentiSynset',
    'TwitterCorpusReader',
    'NKJPCorpusReader',
    'CrubadanCorpusReader',
    'MTECorpusReader',
    'ReviewsCorpusReader',
    'OpinionLexiconCorpusReader',
    'ProsConsCorpusReader',
    'CategorizedSentencesCorpusReader',
    'ComparativeSentencesCorpusReader',
    'PanLexLiteCorpusReader',
    'NonbreakingPrefixesCorpusReader',
    'UnicharsCorpusReader',
    'MWAPPDBCorpusReader',
    'PanlexSwadeshCorpusReader',
]
