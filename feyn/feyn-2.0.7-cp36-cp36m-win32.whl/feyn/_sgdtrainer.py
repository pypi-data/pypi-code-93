import numpy as np
import itertools
import threading
from typing import Callable, Union, Optional, List, Iterable

import _feyn
import feyn

from pandas import DataFrame
import pandas as pd

from feyn._typings import check_types

class PerformanceChangeLog:
    def __init__(self):
        self.table = {}

    def log_models(self, models):
        for m in models:

            d = m._program.data

            record = {
                "action": d["action"],
                "generation": d["generation"],
                "ix": d["ix"],
                "program": m._program._codes[0:len(m._program)],

                "aic": m.aic, 
            }

            parent = self.table.get(d["ppid"])
            if parent:
                record["pprogram"] = parent["program"]
                record["prev"] = record["pprogram"][d["ix"]]
                record["new"] = record["program"][d["ix"]]
                record["aic_diff"] = record["aic"] - parent["aic"]
            else:
                record["pprogram"] = []
                record["prev"] = 0
                record["new"] = 0
                record["aic_diff"] = 0


            self.table[d["pid"]] = record

    def to_df(self):
        df = pd.DataFrame.from_dict(self.table, orient="index")

        # Drop "new" actions
        df = df[df.action!="n"]

        df = df.reset_index(drop=True)
        return df


performance_log = None
def stop_and_get_performance_log():
    global performance_log
    if not performance_log:
        raise RuntimeError("Not currently logging performance. You must call 'start_performance_log' first")

    res = performance_log.to_df()
    performance_log = None
    return res

def start_performance_log():
    global performance_log
    performance_log = PerformanceChangeLog()


@check_types()
def fit_models(
    models: List[feyn.Model],
    data: DataFrame,
    loss_function: Union[str, Callable] = _feyn.DEFAULT_LOSS,
    criterion: Optional[str] = None,
    n_samples: Optional[int] = None,
    sample_weights: Optional[Iterable[float]] = None,
    threads: int = 4,
    immutable: bool = False,
) -> List[feyn.Model]:
    """Fit a list of models on some data and return a list of fitted models. The return list will be sorted in ascending order by either the loss function or one of the criteria.

    The n_samples parameter controls how many samples are used to train each model. The default behavior is to fit each model once with each sample in the dataset, unless the set is smaller than 10000, in which case the dataset will be upsampled to 10000 samples before fitting.

    The samples are shuffled randomly before fitting to avoid issues with the Stochastic Gradient Descent algorithm.


    Arguments:
        models {List[feyn.Model]} -- A list of feyn models to be fitted.
        data {[type]} -- Data used in fitting each model.

    Keyword Arguments:
        loss_function {Union[str, Callable]} -- The loss function to optimize models for. Can take any loss function in `feyn.losses`. (default: {"squared_error"} (MSE))
        criterion {Optional[str]} -- Sort by information criterion rather than loss. Either "aic", "bic" or None. (default: {None})
        n_samples {Optional[int]} -- The number of samples to fit each model with. (default: {None})
        sample_weights {Optional[Iterable[float]]} -- An optional numpy array of weights for each sample. If present, the array must have the same size as the data set, i.e. one weight for each sample. (default: {None})
        threads {int} -- Number of concurrent threads to use for fitting. (default: {4})
        immutable {bool} -- If True, create a copy of each model and fit those, leaving the originals untouched. This increases runtime. (default: {False})

    Raises:
        TypeError: if inputs don't match the correct type.
        ValueError: if there are no samples
        ValueError: if data and sample_weights is not same size
        ValueError: if the loss function is unknown.

    Returns:
        List[feyn.Model] -- A list of fitted feyn models.
    """
    if immutable:
        models = [feyn.Model._from_dict(m._to_dict(include_state=True)) for m in models]

    # Magic support for pandas DataFrame
    data = {col: data[col].values for col in data.columns}

    length = len(next(iter(data.values())))

    if n_samples is None:
        n_samples = max(10000, length)
    if n_samples <= 0:
        raise ValueError("More than 0 samples are required for fitting models.")

    # Create a sequence of indices from the permutated data of length n_samples
    permutation = np.random.permutation(n_samples) % length
    data = {key: values[permutation] for key, values in data.items()}

    if sample_weights is not None:
        # Scale the sample_weights
        sample_weights = np.multiply(list(sample_weights), 1 / max(sample_weights))
        s_size = len(sample_weights)
        if not s_size == length:
            raise ValueError(
                f"The sizes of data ({length}) and sample_weights ({s_size}) do not match."
            )

        # Also permutate the sample_weights
        sample_weights = sample_weights[permutation]

    loss_function = feyn.losses._get_loss_function(loss_function)
    if not hasattr(loss_function, "c_derivative"):
        raise ValueError(
            "Loss function cannot be used for fitting, since it doesn't have a corresponding c derivative"
        )

    _counter = itertools.count()
    _terminate = False
    _exception: BaseException = None

    def fitting_thread():
        nonlocal _terminate, _counter, _exception
        try:
            while not _terminate:
                ix = next(_counter)
                if ix >= len(models):
                    return
                m = models[ix]
                m._fit(data, loss_function, sample_weights)

                if not np.isfinite(m.loss_value):
                    # Model not defined in its entire domain. Ignore it
                    continue

        except BaseException as e:
            _exception = e

    if threads > 1:

        threadlist = [threading.Thread(target=fitting_thread) for _ in range(threads)]
        try:
            [t.start() for t in threadlist]
            while any(t.is_alive() for t in threadlist):
                [t.join(1 / threads) for t in threadlist]
                if _exception:
                    raise _exception
        finally:
            _terminate = True
            [t.join() for t in threadlist]
        if _exception:
            raise _exception

    else:
        # Dont use threading at all if threads = 1, mainly useful for debugging and profiling
        fitting_thread()

    # Remove any models that dont work for the input domain
    models = list(filter(lambda m: np.isfinite(m.loss_value), models))

    for m in models:
        m.bic = feyn.criteria.bic(m.loss_value, m._paramcount, length)
        m.aic = feyn.criteria.aic(m.loss_value, m._paramcount, length)

    if criterion == "bic":
        models.sort(key=lambda m: m.bic, reverse=False)
    elif criterion == "aic":
        models.sort(key=lambda m: m.aic, reverse=False)
    elif criterion is None:
        models.sort(key=lambda m: m.loss_value, reverse=False)
    else:
        raise Exception(
            "Unknown information criterion %s. Must be 'aic', 'bic' or None)"
            % criterion
        )

    for m in models:
        m.age += 1

    global performance_log
    if performance_log is not None:
        performance_log.log_models(models)

    return models
