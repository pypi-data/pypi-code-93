from ._choice_model import ChoiceModel
import numpy as np

class LatentClassModel(ChoiceModel):
    """Class for estimation of Latent Models for Discrete Choice Analysis

    """
    def __init__(self):
        pass

    def fit(self, X, y, varnames=None, alts=None, isvars=None,
            ids=None, weights=None, avail=None, transvars=None, transformation=None,
            base_alt=None, fit_intercept=False, init_coeff=None, maxiter=2000,
            random_state=None, ftol=1e-5, gtol=1e-5, grad=True, hess=True, 
            verbose=1):
        """Fit latent class models

        Parameters
        ----------
        X : array-like, shape (n_samples, n_variables)
            Input data for explanatory variables in long format

        y : array-like, shape (n_samples,)
            Choices in long format

        varnames : list, shape (n_variables,)
            Names of explanatory variables that must match the number and
            order of columns in ``X``

        alts : array-like, shape (n_samples,)
            Alternative indexes in long format or list of alternative names

        isvars : list
            Names of individual-specific variables in ``varnames``

        transvars: list, default=None
            Names of variables to apply transformation on

        ids : array-like, shape (n_samples,)
            Identifiers for choice situations in long format.

        weights : array-like, shape (n_variables,), default=None
            Weights for the choice situations in long format.

        avail: array-like, shape (n_samples,)
            Availability of alternatives for the choice situations. One when
            available or zero otherwise.

        base_alt : int, float or str, default=None
            Base alternative

        fit_intercept : bool, default=False
            Whether to include an intercept in the model.

        init_coeff : numpy array, shape (n_variables,), default=None
            Initial coefficients for estimation.

        maxiter : int, default=200
            Maximum number of iterations

        random_state : int, default=None
            Random seed for numpy random generator

        verbose : int, default=1
            Verbosity of messages to show during estimation. 0: No messages,
            1: Some messages, 2: All messages

        method: string, default="bfgs"
            specify optimisation method passed into scipy.optimize.minimize

        ftol : int, float, default=1e-5
            Sets the tol parameter in scipy.optimize.minimize - Tolerance for
            termination.

        gtol: int, float, default=1e-5
            Sets the gtol parameter in scipy.optimize.minimize(method="bfgs) -
            Gradient norm must be less than gtol before successful termination.

        grad : bool, default=True
            Calculate and return the gradient in _loglik_and_gradient

        hess : bool, default=True
            Calculate and return the gradient in _loglik_and_gradient

        scipy_optimisation : bool, default=False
            Use scipy_optimisation for minimisation. When false uses own
            bfgs method.

        Returns
        -------
        None.
        """
        X, y, initialData, varnames, alts, isvars, transvars, ids, weights, panels, avail \
            = self._as_array(X, y, varnames, alts, isvars, transvars, ids, weights, None, avail)
        self._validate_inputs(X, y, alts, varnames, isvars, ids, weights, None,
                              base_alt, fit_intercept, maxiter)
        self._pre_fit(alts, varnames, isvars, transvars, base_alt,
                      fit_intercept, transformation, maxiter, panels)
        X, y, panels = self._arrange_long_format(X, y, ids, alts)

        self.y = y
        self.initialData = initialData
        self.grad = grad
        self.hess = hess
        self.gtol = gtol
        self.ftol = ftol
        # self.method = method

        jac = True if self.grad else False

        if random_state is not None:
            np.random.seed(random_state)

        if self.transvars is not None and self.transformation is None:
            # if transvars provided and no specified transformation function
            # give default to boxcox
            self.transformation = "boxcox"

        if transformation == "boxcox":
            self.transFunc = boxcox_transformation
            self.transform_deriv = boxcox_param_deriv

        if init_coeff is None:
            betas = np.repeat(.1, self.numFixedCoeffs + self.numTransformedCoeffs)
        else:
            betas = init_coeff
            if len(init_coeff) != (self.numFixedCoeffs + self.numTransformedCoeffs):
                raise ValueError("The size of initial_coeff must be: "
                                 + int(X.shape[1]))

        X, Xnames = self._setup_design_matrix(X)

        if weights is not None:
            weights = weights.reshape(X.shape[0], X.shape[1])

        if avail is not None:
            avail = avail.reshape(X.shape[0], X.shape[1])



        pass

    def _compute_probabilities():
        pass

    def _loglik_gradient():
        pass

    def optimisation():
        pass