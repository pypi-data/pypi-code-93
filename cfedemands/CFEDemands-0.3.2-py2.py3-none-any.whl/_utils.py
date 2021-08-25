# [[file:../Demands/demands.org::demand_utils][demand_utils]]
# Tangled on Wed Aug 25 16:27:34 2021
from scipy import optimize 
from numpy import array, ones, zeros, sum, log, Inf, dot, nan, all, max, abs
import warnings

def check_args(p=None,alpha=None,beta=None,phi=None,tol=1e-12,**extra):
    """
    Perform sanity check on inputs.  Supply default values if these are missing.
    Return an int indicating number of goods and a dictionary of parameters.
    """

    N = []
    # Make sure all args are of type array:
    if p is not None:
        p=array(p,dtype=float)
        N.append(len(p))

    try: 
        len(alpha) # If len() not defined, then must be a singleton
        alpha=array(alpha,dtype=float)
        N.append(len(alpha))
    except TypeError: alpha=array([alpha],dtype=float)

    try:
        len(beta) # If len() not defined, then must be a singleton
        beta = array(beta,dtype=float)
        N.append(len(beta))
    except TypeError: beta = array([beta],dtype=float)

    try:
        len(phi) # If len() not defined, then must be a singleton
        phi=array(phi,dtype=float)
        N.append(len(phi))
    except TypeError: phi=array([phi],dtype=float)

    n = max(N)

    if len(alpha)==1<n:
        alpha=ones(n)*alpha
    else:
        if not alpha.all():
            raise ValueError

    if len(beta)==1<n:
        beta = ones(n)*beta
    else:
        if not beta.all():
            raise ValueError("Problem with beta?")
        if not all(beta>0):
            beta = abs(beta*(beta>0)) + (beta<=0)*tol
            warnings.warn('Setting negative values of beta to zero.')
            #raise ValueError("Non-positive beta?")
    
    if len(phi)==1<n:
        phi=ones(n)*phi

    return n,{'alpha':alpha,'beta':beta,'phi':phi}

def derivative(f,h=2e-5,LIMIT=False):
    """
    Computes the numerical derivative of a function with a single scalar argument.

    - h :: A precision parameter.  

    BUGS: Would be better to actually take a limit, instead of assuming that h 
    is infinitesimal.  
    """
    def df(x, h=h):
        return ( f(x+h/2) - f(x-h/2) )/h
    return df
# demand_utils ends here
