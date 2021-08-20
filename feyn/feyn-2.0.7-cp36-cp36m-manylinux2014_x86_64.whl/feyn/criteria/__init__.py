"""A collection of filters to use with feyn Models."""

import feyn
import numpy as np

def bic(loss_value: float, param_count: int, n_samples: int) -> float:
    return n_samples * np.log(loss_value) + param_count * np.log(n_samples)

def aic(loss_value: float, param_count: int, n_samples: int) -> float:
    return n_samples * np.log(loss_value) + param_count * 2
