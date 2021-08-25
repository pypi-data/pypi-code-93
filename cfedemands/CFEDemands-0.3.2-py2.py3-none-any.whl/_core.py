# [[file:../Demands/demands.org::demand_core][demand_core]]
# Tangled on Wed Aug 25 16:27:34 2021
from . import frischian
from ._utils import check_args, derivative
import warnings
from numpy import nan, Inf, array
from .root_with_precision import root_with_precision

def excess_expenditures(y,p,parms,NegativeDemands=True):
    """
    Return a function which will tell excess expenditures associated with a lambda.
    """
    n,parms = check_args(p=p,**parms)

    def f(lbda):
        lbda=abs(lbda)

        x=frischian.demands(lbda,p,parms,NegativeDemands=NegativeDemands)

        d=0.0
        for i in range(n):
            d += x[i]*p[i]

        return d - y

    return f

def excess_expenditures_derivative(p,parms):
    """
    Return derivative of excess expenditures function with respect to lambda
    """
    n,parms = check_args(p=p,**parms)
    alpha = parms['alpha']
    d = parms['beta']

    def df(lbda):

        lbda=abs(lbda)
        y=0.0
        for i in range(n):
            y += -d[i]*p[i]*(alpha[i]/(p[i]))**(d[i])*lbda**-(1+d[i])

        return y 

    return df

def excess_utility(U,p,parms,NegativeDemands=True):
    """
    Return a function which will tell excess utility associated with a lambda.
    """

    n,parms = check_args(p=p,**parms)

    def f(lbda):

        return U - frischian.V(lbda,p,parms,NegativeDemands=NegativeDemands)

    return f

def lambdavalue(y,p,parms,NegativeDemands=True,ub=10,method='root_with_precision',tol=1e-12):
    """
    Given income y, prices p and preference parameters
    (alpha,beta,phi), find the marginal utility of income lbda.
    """

    n,parms = check_args(p=p,**parms)

    phi = parms['phi']

    if NegativeDemands:
        subsistence=sum([p[i]*phi[i] for i in range(n)])
    else:
        subsistence=sum([p[i]*phi[i] for i in range(n) if phi[i]<0])
    
    if y+subsistence<0: # Income too low to satisfy subsistence demands
        warnings.warn('Income too small to cover subsistence phis (%f < %f)' % (y,subsistence))
        return nan

    f = excess_expenditures(y,p,parms,NegativeDemands=NegativeDemands)

    if method=='bisect':
        try:
            return optimize.bisect(f,tol,ub)
        except ValueError:
            return lambdavalue(y,p,parms,NegativeDemands=NegativeDemands,ub=ub*2.0)
    elif method=='newton':
        df = excess_expenditures_derivative(p,parms)
        return optimize.newton(f,ub/2.,fprime=df)
    elif method=='root_with_precision':
        return root_with_precision(f,[0,ub,Inf],tol,open_interval=True)
    else:
        raise ValueError("Method not defined.")

def lambdaforU(U,p,parms,NegativeDemands=True,ub=10):
    """
    Given level of utility U, prices p, and preference parameters
    (alpha,beta,phi), find the marginal utility of income lbda.
    """

    n,parms = check_args(p=p,**parms)

    f = excess_utility(U,p,parms,NegativeDemands=NegativeDemands)

    # Our root-finder looks within an interval [1e-20,ub].  If root
    # isn't in this interval, optimize.bisect will raise a ValueError;
    # in this case, try again, but with a larger upper bound.
    try:
        #return optimize.bisect(f,1e-20,ub)
        return root_with_precision(f,[0,ub,Inf],1e-12,open_interval=True)
    except ValueError:
        return lambdaforU(U,p,parms,NegativeDemands=True,ub=ub*2.0)

def expenditures(lbda,p,parms,NegativeDemands=True):
    # See https://gist.github.com/datagrok/40bf84d5870c41a77dc6 for this import rationale
    from .hicksian import expenditurefunction

    n,parms = check_args(p=p,**parms)

    U=frischian.indirect_utility(lbda,p,parms,NegativeDemands=NegativeDemands)

    return expenditurefunction(U,p,parms,NegativeDemands=NegativeDemands)

def relative_risk_aversion0(p,parms,NegativeDemands=True,ub=10,method='root_with_precision'):
    """
    Generates function describing (minus) elasticity of lambda w.r.t. expenditures x.

    NB: This is also relative risk aversion.

    DEPRECATED: This has been replaced by a more analytical solution, _core.relative_risk_aversion.
    """
    n,parms = check_args(p=p,**parms)

    lmbda=lambda x: lambdavalue(x,p,parms,NegativeDemands=NegativeDemands,ub=10,method='root_with_precision')
    dl=derivative(lmbda)

    def rra(x):
        return -dl(x)/lmbda(x)*x

    return rra

def relative_risk_aversion(p,parms,NegativeDemands=True):
    """
    Generates function describing (minus) elasticity of lambda w.r.t. expenditures x.

    NB: This is also relative risk aversion.
    """
    from .marshallian import demands as mdemands
    
    n,parms = check_args(p=p,**parms)

    def rra(x):
        return x/(array(mdemands(x,p,parms,NegativeDemands=NegativeDemands))*p).dot(beta)

    return rra
# demand_core ends here
