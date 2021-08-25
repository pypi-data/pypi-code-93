import numpy as np
import scipy.special as special

from .trimerbc import shiftedLJ
from .effectivepotential import twobody_value, twobody_derivative
from .effectivepotential import threebody_value, threebody_derivative_u
from .meshode import meshODE

from samspecialfuncs.bristol.integrals import kappa_12, kappa_6, gamma_12, gamma_6


class wBessel(shiftedLJ):

    
    """
    Evaluate the w(r) function which satisfies the differential
    equation

        w''(r) + 3w'(r)/r - Pi/2*w(r) = V'(r)/(2r), (1)

    with Pi being a constant. w(r) satisfies the boundary conditions
    w(r=infty)=0 and
    
        r_0 w'(r_0) + w(r_0) = -1/denom, (2)

    where r_0 = 2^{1./6.} to first order in f_P, and denom SHOULD
    be 3.0 but could be treated as a fitting parameter

    The full details of the calculation can be found in the doc/
    folder, but essentially, eqn (1) with eqns (2) and (3) can
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

    __init__(self,epsilon=1,denom=3.0)
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
        self.__k1 = self.__k_1()
        self.__k2 = self.__k_2(self.__k1)
        self.__c2 = self.__c_2(self.__k2)


        return


    def __nu_1_integrand(self,s):

        return (special.k1(np.sqrt(self.Pi/2.)*s)
                *self.V_derivative(s)*s)

    def __nu_2_integrand(self,s):

        return (special.i1(np.sqrt(self.Pi/2.)*s)
                *self.V_derivative(s)*s)



    def __coeff_prefacs(self):
        
        Pi = self.Pi
        epsilon = self.epsilon
        t1 =  48*epsilon*Pi**(11./2.)/2**(13./2.)

        t2 = 24*epsilon*Pi**(5./2.)/2**(7./2.)

        
        return t1,t2

    
    def __k_1(self):

        return 0.0

    def __k_2(self,dumk1):

        temp = -1./(self.denom*np.sqrt(self.Pi/2.))

        return temp/special.kvp(1,np.sqrt(self.Pi/2.)*self.r0,1)

    def __c_2(self,dumk2):
        
        temp = -1./(self.denom*np.sqrt(self.Pi/2.))

        return temp/special.kvp(1,np.sqrt(self.Pi/2.)*self.r0,1)
    
    def __nu_1_prime(self,r):

        return 0.5*self.__nu_1_integrand(r)

    def __nu_2_prime(self,r):

        return -0.5*self.__nu_2_integrand(r)

    
    def __nu_1(self,r):

        t1,t2= self.__coeff_prefacs()
        tdel = t1/t2
        x = np.sqrt(self.Pi/2)*r
        x0 = np.sqrt(self.Pi/2)*self.r0
        
        return (self.__k1 +t2*(-tdel*(kappa_12(x)-kappa_12(x0))
                +(kappa_6(x)-kappa_6(x0))))

    def __nu_2(self,r):

        t1,t2= self.__coeff_prefacs()
        tdel = t1/t2
        x = np.sqrt(self.Pi/2)*r
        x0 = np.sqrt(self.Pi/2)*self.r0
        
        return (self.__k2 + t2*(tdel*(gamma_12(x)-gamma_12(x0))
                -(gamma_6(x)-gamma_6(x0))))

    
    def __w_minus(self,r):

        #if abs(self.r0-2**(1./6.)) < 1e-15:

         #   return r*0

        r = np.asarray(r)

        if r.ndim == 2:

            nu1s = meshODE(r,self.__nu_1)
            nu2s = meshODE(r,self.__nu_2)


        else:
            nu1s = self.__nu_1(r)
            nu2s = self.__nu_2(r)
        
        
        return (special.i1(np.sqrt(self.Pi/2.)*r)*nu1s/r
                +special.k1(np.sqrt(self.Pi/2.)*r)*nu2s/r)

    def __w_minus_prime(self,r,flag = None):

        #if abs(self.r0-2**(1./6.)) < 1e-15:

        #    return r*0

        sPi = np.sqrt(self.Pi/2.)

        return (sPi*special.ivp(1,sPi*r,1)
                *self.__nu_1(r)/r
                +special.i1(sPi*r)*self.__nu_1_prime(r)/r
                +sPi*special.kvp(1,sPi*r,1)
                *self.__nu_2(r)/r
                +special.k1(sPi*r)*self.__nu_2_prime(r)/r
                -self.__w_minus(r)/r)

    
    def __w_plus(self,r):
        
        return self.__c2*special.k1(np.sqrt(self.Pi/2.)*r)/r

    def __w_plus_prime(self,r):

        sPi = np.sqrt(self.Pi/2.)

        return (self.__c2*sPi*special.kvp(1,sPi*r,1)/r
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
        
        return np.where(r>=2**(1./6.),self.__w_plus(r),self.__w_minus(r))

    
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
                     self.__w_minus_prime(r))

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

    def Effective2Bod_prime(self,r):
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

if __name__ == "__main__":

    import matplotlib.pyplot as plt
    from scipy.integrate import solve_ivp

    # solve ODE using class defined above
    
    rs = np.linspace(0.8,10,num=5000,endpoint=True)

    fp = 1.0/2**(1./6.)
    epsilon = 10.0
    Pi = 1.0/2**(1./3.)

    ss = wBessel(epsilon=epsilon,Pi=Pi)

    r0 = ss.r0

    # see if BC is satisfied (this should be zero)
    print(ss.w(r0)+r0*ss.w_prime(r0)+1./3.)
    

    # solve ODE numerically for r < 2**(1./6.)
    
    def func(t,y,Pi,epsilon):

        return [y[1],-y[1]/(3*t)+Pi/2.*y[0]+-24*epsilon/t**14+12*epsilon/t**8]


    t_span = (2**(1./6.),0.8)#(0.9,0.8)#

    y0 = [ss.w(t_span[0]),ss.w_prime(t_span[0])]

    
    t_eval = np.concatenate((rs[rs<r0],np.array([r0,2**(1./6.)],float)))[::-1]#rs[rs<0.9][::-1]
    solve = solve_ivp(func,t_span,y0,t_eval=t_eval,args=(Pi,epsilon),method='Radau')

    print(solve.t[1],r0)
    print(solve.y[0][1]+r0*solve.y[1][1]+1./3.)

    
    
    fig,axarr = plt.subplots(4,sharex=True)

    fig.set_size_inches(4,4*3)

    true_w = ss.w(rs)
    num_w = solve.y[0]
    axarr[0].plot(rs,true_w,'k-')
    axarr[0].plot(solve.t,num_w,'r-')

    
    true_p = ss.w_prime(rs)
    num_p = np.gradient(ss.w(rs),rs)
    axarr[1].plot(rs,true_p,'.')
    axarr[1].plot(rs,num_p,'k-')

    print(solve.t[::-1][:-2])
    axarr[2].plot(rs[rs<r0],np.abs((true_w[rs<r0]-num_w[::-1][:-2])/true_w[rs<r0]))
    #axarr[2].plot(rs[rs<0.9],np.abs((true_w[rs<0.9]-num_w[::-1])/true_w[rs<0.9]))
    #    axarr[2].set_yscale('log')
    axarr[2].set_ylim(0,0.2)

    
    
    axarr[3].plot(rs,np.abs(true_p-num_p))
    axarr[3].set_yscale('log')
    axarr[3].set_xlim(0.8,0.9)



    plt.show()
