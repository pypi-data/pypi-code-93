import numpy as np
import scipy.special as special
from scipy.integrate import solve_ivp, solve_bvp

from .trimerbc import shiftedLJ
from .effectivepotential import twobody_value,twobody_derivative
from .meshode import meshODE

class wPerturb(shiftedLJ):

    
    """
    Evaluate the w(r) function which satisfies the differential
    equation

        w''(r) + (3/r - V'(r))w'(r) - (Pi/2 + V'(r)/r)*w(r)
        = V'(r)/(2r),                                       (1)

    with Pi being a constant. w(r) satisfies the boundary conditions
    w(r=infty)=0 and
    
        r_0 w'(r_0) + w(r_0) = -1/denom, (2)

    where r_0 = 2**(1./6.) to first order in f_P, and denom SHOULD
    be 3.0 but could be treated as a fitting parameter.

    The full details of the calculation can be found in the doc/
    folder, but essentially, eqn (1) with eqn (2) can
    be written as integrals over bessel functions. This class then
    computes these integrals using some help from special functions.

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

    __init__(self,epsilon=1,Pi=3.0,denom=3.0)
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
        pre = np.sqrt(Pi/2.0)
        tw = 2**(1./6.)

        # storing a couple local variables to reduce func evaluations.
        self.__k1_tw = special.k1(pre*tw) 
        self.__k1p_tw = special.kvp(1,pre*tw)

        self.__c0 = -1./(self.denom*np.sqrt(self.Pi/2.))/special.kvp(1,np.sqrt(self.Pi/2.)*self.r0,1)


        self.__w_lower = self.__below_r0()

        return

    def __fun(self,r,y,p):

        """
        RHS of y' = f(r,y) for ODE to be solved, with y[0] = w, y[1] = w'.

        Parameters
        ----------

        r : array-like
            independent variable (distance between particles). MUST BE
            LESS THAN 2**(1./6.).
        y : array-like
            dependent variables with y[0] = w, y[1] = w'.
        p : array-like
            list of parameters, which for us is just p = [c0], and is
            only passed to this function as a dummy argument.

        Returns
        ------
        fun : np.array
            RHS of y' = f(r,y) (ODE at r).
        """

        y0 = y[0]
        y1 = y[1]

        y0p = y1
        y1p = (-3*y1/r+self.Pi/2.*y0+
          +self.V_derivative(r)*(y1+y0/r+0.5/r))

        return np.vstack((y0p,y1p))

    def __y0(self):

        """
        At r = 2**(1./6.), continuity enforces that the prefactor c0
        of the r > 2**(1./6.) solution to the ODE, namely,
        w_{+}(r) = special.k1(np.sqrt(self.Pi/2.)*r)/r), be related
        to the prefactors of the solution w_{-}(r) for r<2**(1./6.).
        This function enforces that relationship for arbitrary c0.

        Returns
        -------
        out : list
           Values of w_{-}(r=2**(1./6.)) and w'_{-}(r=2**(1./6.)).

        """

        tw = 2**(1./6.)
        pre = np.sqrt(self.Pi/2.0)
        y0 = self.__c0*special.k1(pre*tw)/2**(1./6.)
        y1 = self.__c0*(pre*special.kvp(1,pre*tw)/tw-special.k1(pre*tw)/tw**2)
        return [y0,y1]


    def __below_r0(self,rf = 0.7):

        y0 = self.__y0()
        t_span = (self.r0,rf)
        # since self.__fun takes a dummy argument, I'll set it to 1
        dum_arg = 1

        res = solve_ivp(self.__fun,t_span,y0,args=(dum_arg,),
                        vectorized=True,dense_output=True)

        return res.sol
    
    def __w_minus_both(self,r):


        r = np.asarray(r)

        if r.ndim == 2:
            
            lowout = meshODE(r,self.__w_lower)


        else:
            lowout = self.__w_lower(r)

        return lowout

    
    def __w_plus(self,r):
        
        return self.__c0*special.k1(np.sqrt(self.Pi/2.)*r)/r

    def __w_plus_prime(self,r):

        sPi = np.sqrt(self.Pi/2.)

        return (self.__c0*sPi*special.kvp(1,sPi*r,1)/r
                - self.__w_plus(r)/r)
                

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
        
        return np.where(r>=2**(1./6.),self.__w_plus(r),
                        self.__w_minus_both(r)[0])

    
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
        

        a = np.where(r>=2**(1./6.),self.__w_plus_prime(r),
                     self.__w_minus_both(r)[1])

        return a

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

        

if __name__ == "__main__":

    import matplotlib.pyplot as plt
    from sambristol_ssabp_w import wBessel
    
    # solve ODE using class defined above
    



    fp = 1.0
    epsilon = 5.0
    ss = wBessel(epsilon=epsilon)
    wperturb = wPerturb(epsilon=epsilon)




    rs = np.linspace(1.0,1.2,num=201)


    plt.plot(rs,wperturb.Effective2Bod(rs),'ro-')

    plt.plot(rs,ss.Effective2Bod(rs),'k--')
    plt.show()

    plt.plot(rs,twobody_derivative(rs,fp,wperturb.w,wperturb.V_value,
                                   wperturb.V_derivative),'ro-')
    plt.plot(rs,twobody_derivative(rs,fp,ss.w,ss.V_value,
                                   ss.V_derivative),'ko-')

    plt.show()
