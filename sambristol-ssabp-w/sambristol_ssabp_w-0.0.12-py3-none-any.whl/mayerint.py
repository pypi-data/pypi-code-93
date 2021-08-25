import numpy as np
import math
from scipy.integrate import romb

class MayerInt():

    """
    This class is focused on computing the integral of the first
    correction in density to the radial distribution function for
    the 2D active brownian particle system with effective two-body
    potential V(r).

    The radial distribution function has the form

        g(r12) = exp(-V(r12))*(1+ rho*c_2(r12) + ...)

    where

        c_2(r12) = \int fmayer(r13)*fmayer(r23) d^2r_3

    and fmayer(r) = (exp(-V(r))-1) is the Mayer function for
    the two-body potential V(r). This class mainly outputs
    the integrand fmayer(r13)*fmayer(r23), and the integral
    c_2(r12) but has other features as well.

    Attributes
    ----------
    twobody : callable function with one argument (position)
        two body potential to use in mayer functions.

    Methods
    -------

    c_2_integral(self,r12s,x1=(0.0,0.0),r3_domain=(0,3.0),
                 r3num = 513, theta3num = 513,
                 check_invariance=False,rtol=1e-5,
                 atol=1e-8,x1_inv=(0.1,0.6)):

        Compute the integral c_2(r12s) from the product
        of two mayer functions.

    g_2(self,rs,rho)

        Simple function to compute approximation to radial
        distribution function accurate to first order in
        density.


    integrand(self,r3,theta_3,x1,x2)

        Compute the integrand of c_2(r12) for polar coordinate
        inputs. Can take np.array inputs and will always output a
        np.array.

    theta_2(self,r12,x1,r2):

        Simple helper function to compute the angle coordinate
        theta2 of particle 2 given that one wants the total 
        distance between particles 1 and 2 to be r12.


    Examples
    --------

    This first example shows how to visualise the integrand using polar
    coordinates plot.

        import matplotlib.pyplot as plt

        from sambristol_ssabp_w.wbessel import wBessel

        fp = 0.5
        epsilon = 1.0
        Pi = 3.0

        ss = wBessel(fp=fp,epsilon=epsilon,Pi=Pi)
        mi = MayerInt(ss.Effective2Bod)

        r12 = 1.0
        r1 = 0.3
        theta1 = 0.0
        r2 = 1.0
        theta2 = mi.theta_2(r12,(r1,theta1),r2)

        r3s = np.linspace(0,3.0,num=513,endpoint=True)
        theta3s = np.linspace(0,2*np.pi,num=513,endpoint=True)

        rs,thetas = np.meshgrid(r3s,theta3s)
        vals = mi.integrand(rs,thetas,(r1,theta1),(r2,theta2))


        fig,ax = plt.subplots(subplot_kw=dict(projection='polar'))
        s = ax.contourf(thetas,rs,vals)
        fig.colorbar(s,ax=ax)

        plt.show()

    The following script demonstrates how one would compute the
    c(r12) integral with this class.

        from scipy.integrate import romb
        from sambristol_ssabp_w.wbessel import wBessel


        fp = 0.5
        epsilon = 1.0
        Pi = 3.0

        ss = wBessel(fp=fp,epsilon=epsilon,Pi=Pi)
        mi = MayerInt(ss.Effective2Bod)

        r12 = 1.0
        r1 = 0.3
        theta1 = 0.0
        r2 = 1.0
        theta2 = mi.theta_2(r12,(r1,theta1),r2)

        r3s = np.linspace(0,3.0,num=513,endpoint=True)
        theta3s = np.linspace(0,2*np.pi,num=513,endpoint=True)

        rs,thetas = np.meshgrid(r3s,theta3s)


        vals = mi.integrand(rs,thetas,(r1,theta1),(r2,theta2))

        integrals = romb(vals,dx = thetas[1,0]-thetas[0,0],axis=0)
        int_final = romb(integrals,dx=rs[0,1]-rs[0,0],show=True)
        print(int_final)

    Note that the integral should be invariant with respect to
    translations and rotations, so that as long as r12 stays
    the same, the integral printed by ''print(int_final)''
    should be the same. This can be confirmed by running the
    following script and comparing to the above one.

        from scipy.integrate import romb
        from sambristol_ssabp_w.wbessel import wBessel


        fp = 0.5
        epsilon = 1.0
        Pi = 3.0

        ss = wBessel(fp=fp,epsilon=epsilon,Pi=Pi)
        mi = MayerInt(ss.Effective2Bod)


        r12 = 1.0
        r1 = 0.1
        theta1 = 0.0
        r2 = 0.9
        theta2 = mi.theta_2(r12,(r1,theta1),r2)

        r3s = np.linspace(0,3.0,num=513,endpoint=True)
        theta3s = np.linspace(0,2*np.pi,num=513,endpoint=True)

        rs,thetas = np.meshgrid(r3s,theta3s)

        
        vals = mi.integrand(rs,thetas,(r1,theta1),(r2,theta2))


        integrals = romb(vals,dx = thetas[1,0]-thetas[0,0],axis=0)
        int_final = romb(integrals,dx=rs[0,1]-rs[0,0],show=True)
        print(int_final)


    Finally, since this is all function based, one could use dbl quad
    integration to compute the integral. This is usually MUCH slower
    than using romb above. Example script is:

        from scipy.integrate import dblquad

        from scipy.integrate import romb
        from sambristol_ssabp_w.wbessel import wBessel


        fp = 0.5
        epsilon = 1.0
        Pi = 3.0

        ss = wBessel(fp=fp,epsilon=epsilon,Pi=Pi)
        mi = MayerInt(ss.Effective2Bod)

        r12 = 1.0
        r1 = 0.3
        theta1 = 0.0
        r2 = 1.0
        theta2 = mi.theta_2(r12,(r1,theta1),r2)


        func = lambda y,x : mi.integrand(x,y,(r1,theta1),(r2,theta2))
    
        int_final = dblquad(func,0,3.0,0,2*np.pi)

        print(int_final)

    All three of these examples should output the same value when
    calling ''print(int_final)''.

    """

    def __init__(self,twobody):

        """
        Initialise class attributes.
        """

        self.twobody = twobody

        return


    def _fmayer(self,rs):

        """
        Compute the Mayer function with effective potential
        w_class.V_value(r) - 0.5*fp**2*w_class.w(r)**2*r**2.
        
        Parameters
        ----------
        rs : float or np.array
            Position(s) to evaluate Mayer function at.
        
        Returns
        -------
        out : np.array
            Mayer function exp(-Veff(r))-1.

        """
        
        Vs = self.twobody(rs)
        return np.where(rs < 0.8,-1,np.exp(-Vs)-1)

    def g_2(self,rs,rho):

        """
        Compute the first two terms in the density expansion
        of the radial distribution function. This function
        is very limited in what it is doing and ignores a lot
        of keyword arguments. The code is just

            prefac = np.exp(- self.twobody(rs))
        
            corr = self.c_2_integral(rs)
        
            return prefac*(1+rho*corr).

        It may be worth writing custom g_2 function with more
        details and e.g. tests of integrand domain using the
        functions self.c_2_integral, self.integrand, etc.

        Parameters
        ----------
        rs : np.array
            Points to evaluate g2 at.
        rho : float
            density of the system.

        Returns
        -------
        out : np.array
            Values exp(-V(rs))*(1+rho*c_2(rs)).
        """
        
        prefac = np.exp(- self.twobody(rs))
        
        corr = self.c_2_integral(rs)
        
        return prefac*(1+rho*corr)

    def c_2_integral(self,r12s,x1=(0.1,0.6),r3_domain=(0,3.0),
                      r3num = 513, theta3num = 513,
                      check_invariance=False,rtol=1e-5,
                      atol=1e-8,x1_inv=(0.3,0.0)):

        """
        Compute the correction factor c_2(r) to the radial
        distribution function at a set of points r12. Useful
        for linear interpolation. c_2(r) is defined as

            g(r) = exp(-V(r))(1+rho*c_2(r))

        where V is the (effective) potential of the system and
        rho is the density. Explicitly,

            c_2(|r12|) = int f(|r13|)*f(|r23|)|r3|d|r3|dtheta3.

        where f(|r|) = e^{-V(|r|)}-1 is the mayer function.

        Parameters
        ----------
        r12s : np.array
            array of distances between particles 1 and 2. should
            not be too close to zero.
        x1 : two-tuple of floats (optional)
            x1=(r1,theta1) is the position of particle 1 when
            computing the integrand. The output should be
            invariant of this positioning, so no need to use
            this option except for in special cases/debugging.
        r3_domain : two-tuple of floats (optional)
            domain of radial integrand. Default is (0,3.0). Should
            check (by plotting integrand) that this domain is large
            enough.
        r3num : int (optional)
            number of points to use in r3 domain when integrating
            (romberg integration, so r3num-1 = 2**k is required).
            Default is 513.
        theta3num : int (optional)
            number of points to use in theta3 domain when integrating
            (romberg integration, so theta3num-1 = 2**k is required).
            Default is 513.
        check_invariance : bool (optional)
            if True, then integrate for different sets of particle
            positions (x1,x2) for each r12 = |x1-x2| to check that
            the resulting integral is the same (it should be).
            Default is false.
        rtol : float (optional)
            positive floating point number to pass to np.allclose
            (only used when check_invariance=True). Default value
            is 1e-5.
        atol : float (optional)
            positive floating point number to pass to np.allclose
            (only used when check_invariance=True). Default value
            is 1e-8.
        x1_inv : two-tuple of floats (optional)
            x1_inv=(r1,theta1) is the position of particle 1 when
            computing the integrand. This is only used when
            check_invariance=True.

        Returns
        ------
        out : np.array
            c_2 evaluated at r12s

        Also, prints a warning if check_invariance=True and the
        integral at each point r12 is not the same for the two
        sets of (x1,x2) positions.
        """

        hss1 = np.empty([len(r12s)],float)

        if check_invariance:
            hss2 = np.empty([len(r12s)],float)
            if np.allclose(x1,x1_inv):
                raise ValueError("The two tuples of points x1 and x1_inv "
                                 "are identical, so check for "
                                 "translational/rotational invariance of "
                                 "the integral is unhelpful.")

        for i,r12 in enumerate(r12s):

            r1 = x1[0]
            theta1 = x1[1]
            r2 = r12+0.99*r1
            theta2 = self.theta_2(r12,(r1,theta1),r2)


            r3s = np.linspace(r3_domain[0],r3_domain[1],num=r3num,
                              endpoint=True)
            theta3s = np.linspace(0,2*np.pi,num=theta3num,
                                  endpoint=True)

            rs,thetas = np.meshgrid(r3s,theta3s)

            vals = self.integrand(rs,thetas,(r1,theta1),(r2,theta2))

            integrals = romb(vals,dx = thetas[1,0]-thetas[0,0],axis=0)
            int_final = romb(integrals,dx=rs[0,1]-rs[0,0])
            hss1[i] = int_final

            if check_invariance:
                # look at another point in the (r1,theta1),(r2,theta2)
                #   plane to see if the answer to the integral is different
                #   (it shouldn't be, since it should only be a function of
                #   |x1-x2| (where x1 and x2 are vectors).
                r1 = x1_inv[0]
                theta1 = x1_inv[1]
                r2 = r12+0.8*r1
                theta2 = self.theta_2(r12,(r1,theta1),r2)

                vals = self.integrand(rs,thetas,(r1,theta1),(r2,theta2))

                integrals = romb(vals,dx = thetas[1,0]-thetas[0,0],axis=0)
                int_final = romb(integrals,dx=rs[0,1]-rs[0,0])

                hss2[i] = int_final


        if check_invariance:

            if not np.allclose(hss1,hss2,rtol=rtol,atol=atol):
                print("error! the integral is not translationally "
                      "invariant!")
                index = np.argmax(np.abs(hss1-hss2))
                rerr = r12s[index]
                maxerr = hss1[index]-hss2[index]
                print(f"maximum error is at r12 = {rerr} "
                      f"taking the value {maxerr}.")

        return hss1

    def integrand(self,r3,theta_3,x1,x2):

        """
        Compute the integrand of c_2(r12) (as described in
        MayerInt.__doc__ string) for polar coordinate inputs
        (includes factor of r3 since d^2r3 = r3*dr3*dtheta_3).
        I.e. 

            fmayer(|r13|)*fmayer(|r23|)*r3

        with
            |rij| = sqrt(ri**2+rj**2-2*ri*rj*cos(theta_i-theta_j)).


        Parameters
        ----------
        r3 : float or np.array
            radial distance of particle 3 to some arbitrary
            origin (is one of the variables to integrate over).
        theta_3 : float or np.array
            polar angle of particle 3 with respect to arbitrary
            origin (is the second variable to integrate over).
        x1 : two-tuple of floats
            polar coordinates x1=(r1,theta1) of particle 1.
        x2 : two-tuple of floats
            polar coordinates x2=(r2,theta2) of particle 2.


        Returns
        -------
        out : np.array
            Product fmayer(|r13|)*fmayer(|r23|)*r3 with
            out.shape having the same shape as the tensor
            product r3\times theta_3 if r3 and theta_3 are
            1D arrays, and having the same shape as r3 
            (or equivalently theta_3) if r3,theta_3 are generated
            from a np.meshgrid.

        """
        
        r1,theta_1 = x1
        r2,theta_2 = x2
    
        r23 = np.sqrt(r3*r3+r2*r2-2*r3*r2*np.cos(theta_3-theta_2))

        r13 = np.sqrt(r3*r3+r1*r1-2*r3*r1*np.cos(theta_3-theta_1))

        return self._fmayer(r23)*self._fmayer(r13)*r3

    def theta_2(self,r12,x1,r2):

        """
        Simple helper function to compute the angle coordinate
        theta2 of particle 2 given that one wants the total 
        distance between particles 1 and 2 to be r12.

            np.arccos(-(r12**2-r1**2-r2**2)/(2*r1*r2))+theta1.

        Parameters
        ----------
        r12 : float or np.array
            specified distance between particles 1 and 2.
        x1 : two-tuple of floats or np.arrays
            polar coordinates x1=(r1,theta1) of particle 1.
        r2 : float or np.array
            radial coordinate of particle 2.

        Returns
        -------
        theta2 : float or np.array
            angle coordinate of particle 2 such that the
            distance between particles 1 and 2 is r12.
        
        """

        r1,theta1=x1
        return np.arccos(-(r12**2-r1**2-r2**2)/(2*r1*r2))+theta1

if __name__ == "__main__":

    import matplotlib.pyplot as plt
    from scipy.integrate import romb
    
    from sambristol_ssabp_w.wbessel import wBessel
    
    fp = 0.5
    epsilon = 1.0
    Pi = 3.0

    ss = wBessel(fp=fp,epsilon=epsilon,Pi=Pi)
    mi = MayerInt(ss.Effective2Bod)

    r12 = 1.0
    r1 = 0.3
    theta1 = 0.0
    r2 = 1.0
    theta2 = mi.theta_2(r12,(r1,theta1),r2)
    
    r3s = np.linspace(0,3.0,num=513,endpoint=True)
    theta3s = np.linspace(0,2*np.pi,num=513,endpoint=True)

    rs,thetas = np.meshgrid(r3s,theta3s)

    
    vals = mi.integrand(rs,thetas,(r1,theta1),(r2,theta2))

    integrals = romb(vals,dx = thetas[1,0]-thetas[0,0],axis=0)
    int_final = romb(integrals,dx=rs[0,1]-rs[0,0],show=True)
    print(int_final)
    

    fig,ax = plt.subplots(subplot_kw=dict(projection='polar'))
    s = ax.contourf(thetas,rs,vals)
    fig.colorbar(s,ax=ax)


    r12 = 1.0
    r1 = 0.1
    theta1 = 0.0
    r2 = 0.9
    theta2 = mi.theta_2(r12,(r1,theta1),r2)

    #rs,thetas = np.meshgrid(r3s,theta3s)

    vals = mi.integrand(rs,thetas,(r1,theta1),(r2,theta2))
    print(mi.integrand(0.4,1.0,(r1,theta1),(r2,theta2)))


    integrals = romb(vals,dx = thetas[1,0]-thetas[0,0],axis=0)
    int_final = romb(integrals,dx=rs[0,1]-rs[0,0],show=True)
    print(int_final)

    fig,ax = plt.subplots(subplot_kw=dict(projection='polar'))
    s = ax.contourf(thetas,rs,vals)
    fig.colorbar(s,ax=ax)


    from scipy.integrate import dblquad


    func = lambda y,x : mi.integrand(x,y,(r1,theta1),(r2,theta2))
    
    int_final = dblquad(func,0,3.0,0,2*np.pi)

    print(int_final)
    
    
    plt.show()

