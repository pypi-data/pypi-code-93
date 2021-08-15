from typing import Dict
import pandas as pd
import numpy as np

from jaison.api import StatisticalAnalysis, ProblemDefinition
from jaison.helpers.numeric import filter_nan
from jaison.helpers.seed import seed
from jaison.data.cleaner import cleaner
from jaison.helpers.log import log
from jaison.api.dtype import dtype
from scipy.stats import entropy
from jaison.data.cleaner import _clean_float_or_none


def get_numeric_histogram(data, data_dtype):
    data = [_clean_float_or_none(x) for x in data]

    Y, X = np.histogram(data, bins=min(50, len(set(data))),
                        range=(min(data), max(data)), density=False)
    if data_dtype == dtype.integer:
        Y, X = np.histogram(data, bins=[int(round(x)) for x in X], density=False)

    X = X[:-1].tolist()
    Y = Y.tolist()

    return {
        'x': X,
        'y': Y
    }


def compute_entropy_biased_buckets(histogram):
    S, biased_buckets = None, None
    if histogram is not None:
        hist_x = histogram['x']
        hist_y = histogram['y']
        nr_values = sum(hist_y)
        S = entropy([x / nr_values for x in hist_y], base=max(2, len(hist_y)))
        if S < 0.25:
            pick_nr = -max(1, int(len(hist_y) / 10))
            biased_buckets = [hist_x[i] for i in np.array(hist_y).argsort()[pick_nr:]]
    return S, biased_buckets


def statistical_analysis(data: pd.DataFrame,
                         dtypes: Dict[str, str],
                         identifiers: Dict[str, object],
                         problem_definition: ProblemDefinition) -> StatisticalAnalysis:
    seed()
    log.info('Starting statistical analysis')
    df = cleaner(data, dtypes, problem_definition.pct_invalid, problem_definition.ignore_features,
                 identifiers, problem_definition.target, 'train', problem_definition.timeseries_settings)

    missing = {col: len([x for x in df[col] if x is None]) / len(df[col]) for col in df.columns}
    distinct = {col: len(set(df[col])) / len(df[col]) for col in df.columns}

    nr_rows = len(df)
    target = problem_definition.target
    # get train std, used in analysis
    if dtypes[target] in [dtype.float, dtype.integer, dtype.array]:
        df_std = df[target].astype(float).std()
    elif dtypes[target] in [dtype.array]:
        try:
            all_vals = []
            for x in df[target]:
                all_vals += x
            df_std = pd.Series(all_vals).astype(float).std()
        except Exception as e:
            log.warning(e)
            df_std = 1.0
    else:
        df_std = 1.0

    histograms = {}
    buckets = {}
    # Get histograms for each column
    for col in df.columns:
        histograms[col] = None
        buckets[col] = None
        if dtypes[col] in (dtype.categorical, dtype.binary):
            hist = dict(df[col].value_counts().apply(lambda x: x / len(df[col])))
            histograms[col] = {
                'x': list(hist.keys()),
                'y': list(hist.values())
            }
            buckets[col] = histograms[col]['x']
        if dtypes[col] in (dtype.integer, dtype.float, dtype.array):
            histograms[col] = get_numeric_histogram(filter_nan(df[col]), dtypes[col])
            buckets[col] = histograms[col]['x']

    # get observed classes, used in analysis
    target_class_distribution = None
    if dtypes[target] in (dtype.categorical, dtype.binary):
        target_class_distribution = dict(df[target].value_counts().apply(lambda x: x / len(df[target])))
        train_observed_classes = list(target_class_distribution.keys())
    elif dtypes[target] == dtype.tags:
        train_observed_classes = None  # @TODO: pending call to tags logic -> get all possible tags
    else:
        train_observed_classes = None

    bias = {}
    for col in df.columns:
        S, biased_buckets = compute_entropy_biased_buckets(histograms[col])
        bias[col] = {
            'entropy': S,
            'description': """Under the assumption of uniformly distributed data (i.e., same probability for Head or Tails on a coin flip) mindsdb tries to detect potential divergences from such case, and it calls this "potential bias". Thus by our data having any potential bias mindsdb means any divergence from all categories having the same probability of being selected.""", # noqa
            'biased_buckets': biased_buckets
        }

    avg_words_per_sentence = {}
    for col in df.columns:
        if dtypes[col] in (dtype.rich_text, dtype.short_text):
            words_per_sentence = []
            for item in df[col]:
                words_per_sentence.append(len(item.split(' ')))
            avg_words_per_sentence[col] = int(np.mean(words_per_sentence))
        else:
            avg_words_per_sentence[col] = None

    log.info('Finished statistical analysis')
    return StatisticalAnalysis(
        nr_rows=nr_rows,
        df_std_dev=df_std,
        train_observed_classes=train_observed_classes,
        target_class_distribution=target_class_distribution,
        histograms=histograms,
        buckets=buckets,
        missing=missing,
        distinct=distinct,
        bias=bias,
        avg_words_per_sentence=avg_words_per_sentence
    )
