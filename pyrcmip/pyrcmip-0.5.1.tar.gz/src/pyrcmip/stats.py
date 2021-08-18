"""
Statistics required for RCMIP analysis
"""
import numpy as np
import scipy.optimize
from scipy.stats import norm


def _diff_exp_sigma(sigma, ratio, conflevel):

    low = (1 - conflevel) / 2
    upp = 1 - low
    qno = norm.ppf(upp)
    ratio_sigma = (np.exp(qno * sigma) - 1) / (1 - np.exp(-qno * sigma))

    diff = ratio_sigma - ratio

    return diff ** 2


def _get_skewed_normal_width(ratio, conflevel):
    ratio_in = ratio if ratio >= 1 else 1 / ratio

    opt_res = scipy.optimize.minimize(
        _diff_exp_sigma,
        (0.1,),
        args=(ratio_in, conflevel),
        bounds=((10 ** -7, 10),),
        options={"maxiter": 10 ** 6},
    )

    if not opt_res.success:
        raise ValueError(
            "Optimisation failed for ratio {} and conflevel {}".format(ratio, conflevel)
        )

    skewed_normal_width = float(opt_res.x.squeeze())

    return skewed_normal_width


def get_skewed_normal(median, lower, upper, conf, input_data):
    """
    Get skewed normal distribution matching the inputs

    Parameters
    ----------
    median : float
        Median of the output distribution

    lower : float
        Lower bound of the confidence interval

    upper : float
        Upper bound of the confidence interval

    conf : float
        Confidence associated with the interval [lower, upper] e.g. 0.66
        would mean that [lower, upper] defines the 66% confidence range

    input_data : :obj:`np.ndarray`
        Points from the derived distribution to return. For each point, Y, in
        ``input_data``, we determine the value at which a cumulative
        probability of Y is achieved. As a result, all values in
        ``input_data`` must be in the range [0, 1]. Hence if you want a random
        sample from the derived skewed normal, simply make ``input_data``
        equal to a random sample of the uniform distribution [0, 1]

    Returns
    -------
    :obj:`np.ndarray`
        Points sampled from the derived skewed normal distribution based on
        ``input_data``
    """
    ratio = (upper - median) / (median - lower)
    ratio_gte_one = ratio >= 1

    skewed_normal_width = _get_skewed_normal_width(ratio, conf)

    factor_denominator = np.exp(skewed_normal_width * norm.ppf(0.5 * (1 + conf))) - 1

    if ratio_gte_one:
        factor = (upper - median) / factor_denominator
    else:
        factor = (lower - median) / factor_denominator

    shift = median - factor

    input_data = np.array(input_data)
    if ratio_gte_one:
        res_inp = input_data
    else:
        res_inp = 1 - input_data

    res = np.exp(norm.ppf(res_inp) * skewed_normal_width) * factor + shift

    return res
