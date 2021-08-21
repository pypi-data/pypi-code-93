import math
from numbers import Real
from typing import List, Dict

try:
    import numpy as np
    from statsmodels.stats.proportion import proportion_confint
    from scipy.stats import t
except ImportError:
    raise ImportError("Install handystuff with stats options: \n\n pip install handystuff[stats]")


def get_mean_var_ci(sample, alpha=0.025):
    sample = np.array(sample)
    t_ci = t.ppf(1 - alpha, df=len(sample) - 1)
    return sample.mean(), sample.var(), t_ci * sample.std() / math.sqrt(len(sample))


def get_mean_var_ci_bernoulli(sample, alpha=0.05):
    if len(sample) > 0:
        lower, _ = proportion_confint(sum(sample), len(sample), alpha=alpha)
        mean = sum(sample) / len(sample)
        return mean, None, mean - lower
    else:
        return 0, None, 0


def mean_dict(result: List[Dict[str, Real]]) -> Dict[str, Real]:
    return {
        k: sum(r[k] for r in result) / len(result) for k in (result[0] if result else {}).keys()
    }
