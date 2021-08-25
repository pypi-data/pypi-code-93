# [[file:../Demands/demands.org::marshallian][marshallian]]
# Tangled on Wed Aug 25 16:27:34 2021
from . import frischian
from ._core import lambdavalue
from ._utils import check_args, derivative
from numpy import array

"""
Marshallian characterization of the CFE demand system taking budget and prices. 
"""

def demands(y,p,parms,NegativeDemands=True):

    n,parms = check_args(p=p,**parms)

    lbda=lambdavalue(y,p,parms,NegativeDemands=NegativeDemands)

    return frischian.demands(lbda,p,parms,NegativeDemands=NegativeDemands)


def indirect_utility(y,p,parms,NegativeDemands=True):
    """
    Returns utils associated with income y and prices p.
    """

    n,parms = check_args(p=p,**parms)

    lbda=lambdavalue(y,p,parms,NegativeDemands=NegativeDemands)

    return frischian.V(lbda,p,parms,NegativeDemands=NegativeDemands)

V = indirect_utility

def expenditures(y,p,parms,NegativeDemands=True,tol=1e-3):

    n,parms = check_args(p=p,**parms)
    
    x=demands(y,p,parms,NegativeDemands=NegativeDemands)

    px=array([p[i]*x[i] for i in range(n)])

    try:
        assert abs(sum(px) - y) < tol
    except AssertionError: # Call to all debugging
        lambdavalue(y,p,parms,NegativeDemands=NegativeDemands)        
    
    return px

def budgetshares(y,p,parms,NegativeDemands=True,tol=1e-3):
    
    n,parms = check_args(p=p,**parms)
    
    x=expenditures(y,p,parms,NegativeDemands=NegativeDemands,tol=tol)

    w=array([x[i]/y for i in range(n)])

    assert abs(sum(w)-1) < tol
    
    return w

def share_income_elasticity(y,p,parms,NegativeDemands=True):
    """
    Expenditure-share elasticity with respect to total expenditures.
    """

    n,parms = check_args(p=p,**parms)

    def w(xbar):
        return budgetshares(xbar,p,parms,NegativeDemands=NegativeDemands)

    dw=derivative(w)

    return [dw(y)[i]*(y/w(y)[i]) for i in range(n)]

def income_elasticity(y,p,parms,NegativeDemands=True):

    return array(share_income_elasticity(y,p,parms,NegativeDemands=NegativeDemands))+1.0
# marshallian ends here
