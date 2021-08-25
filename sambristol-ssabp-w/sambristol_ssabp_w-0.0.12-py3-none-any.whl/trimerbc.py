
class shiftedLJ():

    """
    Simple class which allows for evaluation of Lennard-Jones (LJ)
    potential with value of 0 at 2**(1./6.). For
    r<2**(1./6.), this potential is equivalent to the
    Weeks-Chandler-Anderson potential. Note that length
    is measured in units of sigma. The explicit form of the
    potential is

    V(r) = epsilon*(4*((r)**(-12)-(r)**(-6))+1).


    Attributes
    ----------
    epsilon : float (optional)
        value of the potential strength. Default is 1.

    Methods
    -------

    __init__(self,epsilon=1)
        Initialise attributes.

    V_value(self,r)
        Compute value of potential at r (could be array or scalar).

    V_derivative(self,r)
        Compute derivative of potential at r (could be array or
        scalar).

    """

    def __init__(self,epsilon=1):

        """
        Initialise potential strength epsilon.

        Parameters
        ----------
        epsilon : float (optional)
            value of the potential strength. Default is 1.
        """
        
        
        self.epsilon = epsilon

        return

    def V_value(self,r):
        """
        Compute value of shiftedLJ potential at r.

        Parameters
        ----------
        r : float or np.array
            distance between particles.

        Returns
        -------
        Value of shiftedLJ potential
        """

        
        return self.epsilon*(4*((r)**(-12)-(r)**(-6))+1)
    
    def V_derivative(self,r):
        """
        Compute derivative value of shiftedLJ potential at r.

        Parameters
        ----------
        r : float or np.array
            distance between particles.

        Returns
        -------
        Derivative value of shiftedLJ potential
        """

        
        return -24*self.epsilon*(2*r**(-13)-r**(-7))


import numpy as np
import scipy.optimize as optimize

class TrimerBC(shiftedLJ):

    """
    Class to compute the zero-force distance r0 for a trimer of active
    brownian particles in an equilateral configuration. The
    competition between active and passive forces allows for
    this configuration to be stable. Therefore, both epsilon
    (potential strength) and fp (active force) must be non-zero.
    r0 satisfies

        fp + sqrt(3)*V'(r0) = 0. (1)

    The potential well is a shifted LJ potential, with the form

    V(r) = epsilon*(4*((r)**(-12)-(r)**(-6))+1), r < 2**(1./6.), (2)
    
    and zero otherwise. This potential is inherited from the parent
    class shiftedLJ().

    Child class of shiftedLJ.


    Attributes
    ----------
    fp : float 
        value of active force
    r0 : float
        zero-force distance between particles.

    as well as inherited attribute epsilon from parent class.

    Methods
    -------

    __init__(self,epsilon=1)
        Initialise fp and compute r0.

    as well as inherited methods V_value and V_derivative from
    parent class.

    """

    
    def __init__(self,fp,epsilon=1):
        """
        Initialise fp and compute r0.

        Parameters
        ----------
        fp : float
            active force strength.
        epsilon : float
            potential well strength.

        """

        super().__init__(epsilon=epsilon)
        
        self.fp = fp
        self.__a0 = self.__a_0()
        if fp <= 0:
            raise ValueError("Active force must be greater than zero.")
        self.r0 = self.__r_0()
        
        return

    def __a_0(self):
        """

        Returns
        -------
        a0 : float
            Dimensionless constant fp/(24*np.sqrt(3)*epsilon).

        """

        return self.fp/(24*np.sqrt(3)*self.epsilon)

    def __r_0_large_a_0(self):
        """
        
        Returns
        -------
        r_0 : float
            Approximate value of r0 when fp >> epsilon.

        """

        q = (2**(7./6.)*self.__a0)**(-1/13)
        p = (2**(7./6.)*self.__a0)**(-6/13)
        f7 = 13-7*p
        g4 = 13-4*p
        
        return 2**(1./6.)*q*(1+1/14*f7/g4*(1-np.sqrt(1+28*p*g4/f7**2)))

    def __r_0_small_a_0(self):
        """
        
        Returns
        -------
        r_0 : float
            Approximate value of r0 when fp << epsilon.

        """

        return 2**(1./6.)*(1+1/21*(1-np.sqrt(1+7*(2**(7./6.)*self.__a0))))

    
    def __r_0_approx(self):
        """
        
        Returns
        -------
        r_0 : float
            Approximate value of r0 to first order in either fp/epsilon
            or epsilon/fp depending on which is the small parameter.

        """
        

        if self.__a0 < 2**(-7./6.):

            r0 = self.__r_0_small_a_0()

        else:

            r0 = self.__r_0_large_a_0()

        return r0

    
    def __forcebalance(self,r):
        """
        Compute force on a trimer of particles in an equilateral configuration,
        where the force is given by

                fp + sqrt(3)*V'(r0).

        Returns
        -------
        force : float
            force on trimer

        """
        
        
        return self.fp + np.sqrt(3)*self.V_derivative(r)

    def __r_0(self):
        """
        Compute the distance between particles in an equilateral trimer
        configuration where the force is zero.

        Returns
        -------
        r0 : float
            distance between particles in the trimer where force is zero.

        """

        r0 = self.__r_0_approx()

        if abs(r0-2**(1./6.))>1e-14:

            r0 = optimize.newton(self.__forcebalance,r0)

        return r0
    

if __name__ == "__main__":

    # test shiftedLJ derivative
    import matplotlib.pyplot as plt
    import numpy as np

    rs = np.logspace(-0.2,0.2,num=10000,endpoint=True)

    cp = shiftedLJ()

    fig,axarr = plt.subplots(3,sharex=True)

    fig.set_size_inches(4,4*2)

    axarr[0].plot(rs,cp.V_value(rs))

    true_p = cp.V_derivative(rs)
    num_p = np.gradient(cp.V_value(rs),rs)
    axarr[1].plot(rs,true_p,'.')
    axarr[1].plot(rs,num_p,'k-')

    axarr[2].plot(rs[1:],np.abs(true_p-num_p)[1:],'o')
    axarr[2].set_yscale('log')

    plt.show()


    # test shift
    fp = 1.0
    tr = TrimerBC(fp)

    fig,ax = plt.subplots()

    fig.set_size_inches(4,4)

    ax.plot(rs,tr._TrimerBC__forcebalance(rs))
    
    ax.plot(tr.r0,tr._TrimerBC__forcebalance(tr.r0),'ko')

    plt.show()
