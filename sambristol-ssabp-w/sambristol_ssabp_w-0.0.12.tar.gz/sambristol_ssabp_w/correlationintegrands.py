from scipy.interpolate import interp1d
import numpy as np


class CorrelationIntegrands():

    """
    Class to compute different integrands of correlation
    functions for a specified x. In particular, the
    integrands:

        B2(x,f) = w(x)*x**2*f(x)*g2(x),            (1)

        B3(x,f) = x*f(x)*\int dv v**2*w(v)*g3(v,x), (2)

        P2(x,f) = x**2*f(x)*g2(x),                 (3)

        C2(x,f) = x**3*f(x)*w(x)**2*g2(x)          (4)

        xi2 = \int [V'(x)]^2 g2(x)*x*dx            (5)

        xi3 = \int\int V'(x)*V'(y)*x*y*g3(x,y)*dx*dy     (6)


    and the 2D integrand (no interpolating option here)

        Q3(u,v) = v**2*w(v)*g3(u,v).               (5)


    In the above, f(x) is some arbitrary function (typically
    either WCA potential or delta function), and w(x) is
    some function (usually the wfunc of our abp system).
    g2 and g3 are the two-body and
    angle-integrated three-body correlation functions,
    respectively.

    Note: If wanting to compute \int dx B(x,f) where
    f(x) = delta^2(x-y)*g(x) is a 2D delta function, just
    set f = lambda x : 1.0 and don't integrate over x. So
    \int dx B(x,delta^2(x-y)*g(x)) = B(y,g(y)).

    Attributes
    ----------
    
    w : callable function
        Typically should be the function w from the wBessel or
        wPerturb class.
    r2s : np.array of shape (bins_2,)
        Array of points where two-body correlation function is
        sampled.
    g2s : np.array of shape (bins_2,)
        Values of two-body correlation function, sampled at
        the points self.r2s.
    r3s : np.array of shape (bins_3,)
        Array of points such that np.meshgrid(r3s,r3s) will
        give the domain where three-body correlation function
        is sampled.
    G3s : np.array of shape (bins_3,bins_3)
        Values of three-body correlation function, sampled at
        the points np.meshgrid(self.r3s,self.r3s)
    Pi : float (optional)
        Value of D_r/D_t. Default is 3.0.
    epsilon : float (optional)
        Value of the WCA interaction potential strength.
        Default is 1.0.

    Methods
    -------
    B2(self,x,f,interpkind='cubic')

    B3(self,x,f,interpkind='cubic')

    Q3(self,insert_zeros=False)

    P2(self,x,f,interpkind='cubic')

    xi2(self,Vprime)

    xi3(self, Vprime)


    """

    def __init__(self,wfunc,r2s,g2s,r3s,G3s):

        """
        Initialise attributes.

        Parameters
        ----------
        w : callable function
            Typically should be the function w from the wBessel or
            wPerturb class.
        r2s : np.array of shape (bins_2,)
            Array of points where two-body correlation function is
            sampled.
        g2s : np.array of shape (bins_2,)
            Values of two-body correlation function, sampled at
            the points self.r2s.
        r3s : np.array of shape (bins_3,)
            Array of points such that np.meshgrid(r3s,r3s) will
            give the domain where three-body correlation function
            is sampled.
        G3s : np.array of shape (bins_3,bins_3)
            Values of three-body correlation function, sampled at
            the points np.meshgrid(self.r3s,self.r3s)


        """            
        self.w = wfunc
        self.r2s = r2s
        self.g2s = g2s
        self.r3s = r3s
        self.G3s = G3s
        
        return


    def B2(self,x,f,interpkind='cubic'):
        """
        Compute the function

            B2(x,f) = w(x)*x**2*f(x)*g2(x).

        Parameters
        ----------
        x : float or np.array of shape(lenx,)
            Points to evaluate B2 at.
        f : callable function
            Function to compute B2 with.
        interpkind : string (optional)
            What kind of interpolation is used. Default
            is 'cubic'.

        Returns
        -------
        out : float or np.array of shape(lenx,)
           Value of B2 at the points in x.
        """

        raw = self.r2s**2*f(self.r2s)*self.w(self.r2s)*self.g2s
        raw[np.isnan(raw)] = 0.0
        fl = interp1d(self.r2s,raw,kind=interpkind)
        return fl(x)

    def B3(self,x,f,interpkind='cubic'):
        """
        Compute the function

            B3(x,f) = x*f(x)*\int dv v**2*w(v)*g3(v,x).

        Parameters
        ----------
        x : float or np.array of shape(lenx,)
            Points to evaluate B3 at.
        f : callable function
            Function to compute B3 with.
        interpkind : string (optional)
            What kind of interpolation is used. Default
            is 'cubic'.

        Returns
        -------
        out : float or np.array of shape(lenx,)
           Value of B3 at the points in x.
        """
        

        UU,VV,integrand = self.Q3(insert_zeros=True)

        dv = VV[1,0]-VV[0,0]

        vals = np.sum(integrand,axis=0)*dv


        raw = self.r3s*f(self.r3s)*vals

        fl = interp1d(self.r3s,raw,kind=interpkind)
        return fl(x)

    def P2(self,x,f,interpkind='cubic'):
        """
        Compute the function

            P2(x,f) = x**2*f(x)*g2(x).

        Parameters
        ----------
        x : float or np.array of shape(lenx,)
            Points to evaluate P2 at.
        f : callable function
            Function to compute P2 with.
        interpkind : string (optional)
            What kind of interpolation is used. Default
            is 'cubic'.

        Returns
        -------
        out : float or np.array of shape(lenx,)
           Value of P2 at the points in x.
        """

        raw = self.r2s**2*f(self.r2s)*self.g2s
        raw[np.isnan(raw)] = 0.0
        fl = interp1d(self.r2s,raw,kind=interpkind)
        return fl(x)

    def C2(self,x,f,interpkind='cubic'):
        """
        Compute the function

            C2(x,f) = x**3*f(x)*w(x)**2*g2(x).

        Parameters
        ----------
        x : float or np.array of shape(lenx,)
            Points to evaluate C2 at.
        f : callable function
            Function to compute C2 with.
        interpkind : string (optional)
            What kind of interpolation is used. Default
            is 'cubic'.

        Returns
        -------
        out : float or np.array of shape(lenx,)
           Value of C2 at the points in x.
        """

        raw = self.r2s**3*f(self.r2s)*self.w(self.r2s)**2*self.g2s
        raw[np.isnan(raw)] = 0.0
        fl = interp1d(self.r2s,raw,kind=interpkind)
        return fl(x)

    def Q3(self,insert_zeros=False):

        """
        Compute the function

                Q3(u,v) = v**2*w(v)*g3(u,v)

        at the discrete points u,v = np.meshgrid(self.rs,self.rs)
        (no interpolation option for this function).


        Parameters
        ----------
        insert_zeros : bool (optional)
            Insert zeros where the nans of self.G3s are.
            Should be set to true if interpolating this
            function. Default is False.
            

        Returns
        -------
        out : list of 3 np.arrays 
           First two items of list are
           np.meshgrid(self.rs,self.rs), third item of list is
           the value of Q3 at the discrete points

        """

        XX,YY = np.meshgrid(self.r3s,self.r3s)

        prod = self.G3s*self.w(YY)*YY*YY

        if insert_zeros:
            prod[np.isnan(prod)] = 0.0

        return XX, YY, prod

    def xi2(self,Vprime):
        """
        Compute the constant 

        xi2 = \int [V'(x)]^2 g2(x)*x*dx.


        Parameters
        ----------
        Vprime : callable function
            Derivative of pairwise WCA potential.

        Returns
        -------
        out : float
           Value of constant for specified Vprime.
        """

        
        raw = self.r2s* Vprime(self.r2s) * Vprime(self.r2s)*self.g2s
        raw[np.isnan(raw)] = 0.0
        dx = self.r2s[1]-self.r2s[0]

        return np.sum(raw)*dx

    def xi3(self,Vprime):
        """
        Compute the function

        xi3 = \int\int V'(x)*V'(y)*x*y*g3(x,y)*dx*dy


        Parameters
        ----------
        Vprime : callable function
            Derivative of pairwise WCA potential.

        Returns
        -------
        out : float
           Value of constant for specified Vprime.
        """

        

        UU,VV = np.meshgrid(self.r3s,self.r3s)

        integrand = self.G3s*Vprime(UU)*Vprime(VV)*UU*VV
        integrand[np.isnan(integrand)] = 0.0

        dv = VV[1,0]-VV[0,0]
        du = UU[0,1]-UU[0,0]

        return np.sum(np.sum(integrand,axis=0))*dv*du



    
if __name__ == "__main__":

    
    import matplotlib.pyplot as plt

    import pickle
    from sambristol_ssabp_w import wBessel,wPerturb

