import statsmodels.api as sm
import statsmodels.formula.api as smf
import numpy as np
import pandas
import scipy as sp
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures

esti_draws = 5
param_dims = 18
poly_dims = 3
X = np.arange(esti_draws*param_dims).reshape(esti_draws, param_dims)
poly = PolynomialFeatures(poly_dims)
poly_expand = poly.fit_transform(X)
print(np.shape(poly_expand)[1])
# poly = PolynomialFeatures(interaction_only=True)
# poly.fit_transform(X)

p0 = 1
p1 = param_dims
p2 = ((sp.math.factorial(param_dims))/(sp.math.factorial(param_dims-poly_dims+1)*sp.math.factorial(poly_dims-1))) + p1
p33 = ((sp.math.factorial(param_dims))/(sp.math.factorial(param_dims-poly_dims)*sp.math.factorial(poly_dims))) + param_dims*(param_dims-1) + p1

ptotal = p0 + p1 + p2 + p33
print(ptotal)
