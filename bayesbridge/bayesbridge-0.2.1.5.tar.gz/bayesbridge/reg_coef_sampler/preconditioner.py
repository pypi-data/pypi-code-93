from functools import wraps
import numpy as np

@staticmethod
def precondition_logp_and_grad_by_scaling(
        compute_logp_and_grad, scale, jacobian_adjusted=True):
    """
    Decorate a function for computing the log-density and gradient so that
    it acts on the scaled parameter `param / scale`.

    Parameters
    ----------
    compute_logp_and_grad(parameter, loglik_only): callable
    scale: ndarray
    jacobian_adjusted: bool
        If `True`, includes the Jacobian factor due to the transformation
        `(param, scale) -> (param / scale, scale)`. Set to `False` if
        preconditioning a likelihood.
    """

    @wraps(compute_logp_and_grad)
    def f(param_scaled, loglik_only=False):
        param = scale * param_scaled
        logp, grad = compute_logp_and_grad(param, loglik_only)
        if not loglik_only:
            grad *= scale  # Chain rule
        if jacobian_adjusted:
            log_det = - np.sum(scale)
            logp += log_det
        return logp, grad

    return f

def adjust_for_logtransform(logp, grad, param, log_param):
    # Chain rule
    grad *= param
    # Jacobian adjustment
    logp += np.sum(log_param)
    grad += 1.
    return logp, grad