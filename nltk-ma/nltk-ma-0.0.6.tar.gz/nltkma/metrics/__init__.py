# Natural Language Toolkit: Metrics
#
# Copyright (C) 2001-2021 NLTK Project
# Author: Steven Bird <stevenbird1@gmail.com>
#         Edward Loper <edloper@gmail.com>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT
#

"""
NLTK Metrics

Classes and methods for scoring processing modules.
"""

from nltkma.metrics.scores import (
    accuracy,
    precision,
    recall,
    f_measure,
    log_likelihood,
    approxrand,
)
from nltkma.metrics.confusionmatrix import ConfusionMatrix
from nltkma.metrics.distance import (
    edit_distance,
    edit_distance_align,
    binary_distance,
    jaccard_distance,
    masi_distance,
    interval_distance,
    custom_distance,
    presence,
    fractional_presence,
)
from nltkma.metrics.paice import Paice
from nltkma.metrics.segmentation import windowdiff, ghd, pk
from nltkma.metrics.agreement import AnnotationTask
from nltkma.metrics.association import (
    NgramAssocMeasures,
    BigramAssocMeasures,
    TrigramAssocMeasures,
    QuadgramAssocMeasures,
    ContingencyMeasures,
)
from nltkma.metrics.spearman import (
    spearman_correlation,
    ranks_from_sequence,
    ranks_from_scores,
)
from nltkma.metrics.aline import align
