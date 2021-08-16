# Natural Language Toolkit: Machine Translation
#
# Copyright (C) 2001-2021 NLTK Project
# Author: Steven Bird <stevenbird1@gmail.com>, Tah Wei Hoon <hoon.tw@gmail.com>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

"""
Experimental features for machine translation.
These interfaces are prone to change.
"""

from nltkma.translate.api import AlignedSent, Alignment, PhraseTable
from nltkma.translate.ibm_model import IBMModel
from nltkma.translate.ibm1 import IBMModel1
from nltkma.translate.ibm2 import IBMModel2
from nltkma.translate.ibm3 import IBMModel3
from nltkma.translate.ibm4 import IBMModel4
from nltkma.translate.ibm5 import IBMModel5
from nltkma.translate.bleu_score import sentence_bleu as bleu
from nltkma.translate.ribes_score import sentence_ribes as ribes
from nltkma.translate.meteor_score import meteor_score as meteor
from nltkma.translate.metrics import alignment_error_rate
from nltkma.translate.stack_decoder import StackDecoder
from nltkma.translate.nist_score import sentence_nist as nist
from nltkma.translate.chrf_score import sentence_chrf as chrf
from nltkma.translate.gale_church import trace
from nltkma.translate.gdfa import grow_diag_final_and
from nltkma.translate.gleu_score import sentence_gleu as gleu
from nltkma.translate.phrase_based import extract
