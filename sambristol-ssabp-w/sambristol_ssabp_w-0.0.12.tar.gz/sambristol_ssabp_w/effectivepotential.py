import numpy as np

"""

Calculate effective potentials for ABP system, given a
specific w-function.

Methods
-------

twobody_value(r)
    
twobody_derivative(r)
    
threebody_value(u,v)

threebody_derivative_u(u,v)

"""


def twobody_value(r,fp,w,V_value):

    """
    Compute effective two-body potential.

    Parameters
    ----------
    r : float or np.array
        Position to compute effective two-body potential at.
    fp : float
        Self-propulsion force.
    w : scalar function with call signature w(r)
        Calculated via the perturbative FP equation.
    V_value : scalar function with call signature V_value(r)
        Conservative potential (e.g. WCA interaction).

    Returns
    -------
    out : float or np.array
        out is V_value(r)-0.5*fp**2*r**2*w(r)**2 when r<2**(1./6.),
        and -0.5*fp**2*r**2*w(r)**2 otherwise.

    """

    out2 = -0.5*fp**2*w(r)**2*r**2
    out1 = V_value(r) + out2

    return np.where(r<2**(1./6.),out1,out2)

def twobody_derivative(r,fp,w,w_prime,V_derivative):


    """
    Compute derivative of effective two-body potential.

    Parameters
    ----------
    r : float or np.array
        Position to compute effective two-body potential at.
    fp : float
        Self-propulsion force.
    w : scalar function with call signature w(r)
        Calculated via the perturbative FP equation.
    w_prime : scalar function with call signature w_prime(r)
        Derivative of w(r).
    V_derivative : scalar function with with call signature V_derivative(r)
        Derivative of V_value(r).

    Returns
    -------
    out : float or np.array
        out is V_derivative(r) - fp**2*(r*w(r)**2 + r**2*w(r)*w_prime(r))
        when r < 2**(1./6.), and 
        -fp**2*(r*w(r)**2 + r**2*w(r)*w_prime(r)) otherwise.

    """



    out2 = -fp**2*(r*w(r)**2 + r**2*w(r)*w_prime(r))
    out1 = V_derivative(r) + out2

    return np.where(r<2**(1./6.),out1,out2)

def threebody_value(u,v,fp,w):


    """
    Compute effective three-body potential without the
    cosine factor.

    Parameters
    ----------
    u : float or np.array
        Position of first particle
    v : float or np.array
        Position of second particle
    fp : float
        Self-propulsion force.
    w : scalar function with call signature w(r)
        Calculated via the perturbative FP equation.

    Returns
    -------
    out : float or np.array
        out is -3./2.*fp**2*u*v*w(u)*w(v)

    """




    return -3./2.*fp**2*u*v*w(u)*w(v)

def threebody_derivative_u(u,v,fp,w,w_prime):

    """
    Compute effective two-body potential, i.e.

        V_value(r)-0.5*fp**2*r**2*w(r)**2.



    Parameters
    ----------
    u : float or np.array
        Position of first particle
    v : float or np.array
        Position of second particle
    fp : float
        Self-propulsion force.
    w : scalar function with call signature w(r)
        Calculated via the perturbative FP equation.
    w_prime : scalar function with call signature w_prime(r)
        Derivative of w(r).

    Returns
    -------
    out : float or np.array
        out is -3./2.*fp**2*(v*w(u)*w(v) + u*v*w_prime(u)*w(v)).

    """

    return -3./2.*fp**2*(v*w(u)*w(v) + u*v*w_prime(u)*w(v))
