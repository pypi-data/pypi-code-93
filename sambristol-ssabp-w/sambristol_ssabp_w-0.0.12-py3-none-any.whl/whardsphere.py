import numpy as np
import scipy.special as special

from .trimerbc import shiftedLJ
from .effectivepotential import twobody_value, twobody_derivative
from .effectivepotential import threebody_value, threebody_derivative_u


class wHardSphere(shiftedLJ):

    
    """
    Evaluate the w(r) function which satisfies the differential
    equation

        w''(r) + 3w'(r)/r - Pi/2*w(r) = 0, (1)

    with Pi being a constant. w(r) satisfies the boundary conditions
    w(r=infty)=0 and
    
        r_0 w'(r_0) + w(r_0) = -1/denom, (2)

    where r_0 = 2**(1./6.) to first order in f_P, and denom SHOULD
    be 3.0 but could be treated as a fitting parameter.

    The above equations can be solved analytically.

    Child class of shiftedLJ.

    Attributes
    ----------
    Pi : float (optional)
        value of the parameter Pi in eqn 1 above. Default value is 3.

    denom : float (optional)
        value of fitting parameter. No-fit parameter defaults to 3.

    

    as well as inherited attributes epsilon from parent class.

    Methods
    -------

    __init__(self,epsilon=1,sigma=3.0,denom = 3.0)
        Initialise attributes.


    w(self,r)
        Compute the solution to the ode mentioned in the class doc.

    
    w_prime(self,r)
        Compute the derivative of the solution to the ode mentioned in
        the class doc.

    """


    def __init__(self,epsilon=1,Pi=3.0,denom=3.0):

        """
        Initialise attributes.

        Parameters
        ----------
        epsilon : float (optional)
            strength of the potential V(r). Default value is 1.
        Pi : float (optional)
            value of the parameter Pi (=D^r*sigma**2/D_t).
            Default value is 3.
        denom : float (optional)
            value of fitting parameter. No-fit parameter defaults to 3.
        """

        super().__init__(epsilon=epsilon)

        self.Pi = Pi
        self.r0 = 2**(1./6.)
        self.denom = denom
        return



    def w(self,r):
        """

        Compute the solution to the ode mentioned in the class doc.

        Parameters
        ----------
        r : float or np.array
            Distance between particles.

        Returns
        -------
        value : float or np.array
            Value of the w-function.

        """
        
        return np.where(r>=2**(1./6.),
                        -np.sqrt(2/self.Pi)*special.k1(np.sqrt(self.Pi/2.)*r)
                        /(self.denom*special.kvp(1,np.sqrt(self.Pi/2.)*self.r0,1)*r),
                        0)

    
    def w_prime(self,r):
        """

        Compute the derivative of the solution to the ode mentioned in
        the class doc.

        Parameters
        ----------
        r : float or np.array
            Distance between particles.

        Returns
        -------
        value : float or np.array
            Value of the w-function derivative.

        """

        return np.where(r>=2**(1./6.),
                        1.0/(self.denom*special.kvp(1,np.sqrt(self.Pi/2.)*self.r0,1)*r)
                        *(-special.kvp(1,np.sqrt(self.Pi/2.)*r,1)/r
                          +np.sqrt(2/self.Pi)*special.k1(np.sqrt(self.Pi/2.)*r)/r**2),0)

    def Effective2Bod(self,r,fp):
        """

        Compute the effective two-body interaction.

        Parameters
        ----------
        r : float or np.array
            Distance between particles.
        fp : float
            value of the active force.

        Returns
        -------
        value : float or np.array
            Value of the effective interaction at r.

        """

        

        return twobody_value(r,fp,self.w,self.V_value)

    def Effective2Bod_prime(self,r,fp):
        """

        Compute the derivative of the effective
        two-body interaction.

        Parameters
        ----------
        r : float or np.array
            Distance between particles.
        fp : float
            value of the active force.

        Returns
        -------
        value : float or np.array
            Derivative of the effective interaction at r.

        """
        

        return twobody_derivative(r,fp,self.w,
                                  self.w_prime,
                                  self.V_derivative)

    def Effective3Bod(self,u,v,fp):
        """

        Compute the effective three-body interaction aside
        from a cosine factor.

        Parameters
        ----------
        u : float or np.array
            Distance between particles 1 and 2.
        v: float or np.array
            Distance between particles 1 and 3.
        fp : float
            value of the active force.

        Returns
        -------
        value : float or np.array
            Value of the effective interaction at u,v.

        """
        

        return threebody_value(self,u,v,fp,self.w)

    def Effective3Bod_prime_u(self,u,v,fp):

        """

        Compute the effective three-body interaction aside
        from a cosine factor.

        Parameters
        ----------
        u : float or np.array
            Distance between particles 1 and 2.
        v: float or np.array
            Distance between particles 1 and 3.
        fp : float
            value of the active force.

        Returns
        -------
        value : float or np.array
            Derivative of the effective interaction at u,v.

        """
        

        return threebody_derivative_u(self,u,v,fp,
                                      self.w,self.w_prime)

