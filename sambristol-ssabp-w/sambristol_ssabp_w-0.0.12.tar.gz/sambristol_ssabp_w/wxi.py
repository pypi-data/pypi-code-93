import numpy as np
import scipy.special as special
from scipy.integrate import solve_ivp, solve_bvp
from scipy.interpolate import interp1d
from .trimerbc import shiftedLJ
from .effectivepotential import twobody_value,twobody_derivative
from .meshode import meshODE
from .whardsphere import wHardSphere

class wXi(shiftedLJ):

    
    """
    Evaluate the average w(r) function which satisfies the 
    stochastic differential equation

        w''(r) + (3/r - V'(r)-xi)w'(r) 
        - (Pi/2 + V'(r)/r+xi/r)*w(r) = V'(r)/(2r),    (1)

    with Pi being a constant, and xi being a random variable,
    which is assumed to be Gaussian.
    w(r) satisfies the boundary conditions w(r=infty)=0 and
    
        r_0 w'(r_0) + w(r_0) = -1/denom, (2)

    where r_0 = 2**(1./6.) to first order in f_P, and denom SHOULD
    be 3.0 but could be treated as a fitting parameter.

    Child class of shiftedLJ.

    Attributes
    ----------
    xi_variance : float
        variance of the distribution for generating xi values.

    xis : float
        list of all xi samples used to generate average w and w'

    Pi : float (optional)
        value of the parameter Pi in eqn 1 above. Default value is 3.

    denom : float (optional)
        value of fitting parameter. No-fit parameter defaults to 3.
    
    rinfty : float (optional)
        large r value which approximates infinity in the BVP for w.
        Default value is 60.

    bvpmesh : float (optional)
        number of mesh points between r0 and rinfty. Default is 10001.

    rlowlim : float (optional)
        lower value of w(r) domain. Default is 0.7.
    noisetype : string (optional)
        choose the type of noise used to generate xi values. Only
        acceptable inputs are "gaussian" or "uniform". Default
        is "gaussian".
    num_rns : int (optional)
        number of times to sample xi from distribution. Default is 1000.

    as well as inherited attributes epsilon from parent class.

    Methods
    -------

    __init__(self,xi_variance,epsilon=1,Pi=3.0,denom=3.0,
             rinfty = 60)
        Initialise attributes.


    w(self,r)
        Compute the solution to the ode mentioned in the class doc.

    
    w_prime(self,r)
        Compute the derivative of the solution to the ode mentioned in
        the class doc.

    """


    def __init__(self,xi_variance,epsilon=1,Pi=3.0,denom=3.0,
                 rinfty = 60,bvpmesh=10001,rlowlim=0.7,
                 noisetype="gaussian",
                 num_rns=1000):

        """
        Initialise attributes.

        Parameters
        ----------

        xi_variance: float
            variance of the distribution for generating xi values.
        epsilon : float (optional)
            strength of the potential V(r). Default value is 1.
        Pi : float (optional)
            value of the parameter Pi (=D^r*sigma**2/D_t).
            Default value is 3.
        denom : float (optional)
            value of fitting parameter. No-fit parameter defaults to 3.
        rinfty : float (optional)
            large r value which approximates infinity in the BVP for w.
            Default value is 60.
        bvpmesh : float (optional)
            number of mesh points between r0 and rinfty. Default is 10001.
        rlowlim : float (optional)
            lower value of w(r) domain. Default is 0.7.
        noisetype : string (optional)
            choose the type of noise used to generate xi values. Only
            acceptable inputs are "gaussian" or "uniform". Default
            is "gaussian".
        num_rns : int (optional)
            number of times to sample xi from distribution. Default is 1000.
        """

        super().__init__(epsilon=epsilon)

        self.xivar = xi_variance
        self.Pi = Pi
        self.r0 = 2**(1./6.)
        self.denom = denom
        self.rinfty = rinfty
        self.bvpmesh = bvpmesh
        self.rlowlim = rlowlim

        self.noisetype = noisetype
        self.num_rns = num_rns
        self.hs = wHardSphere(epsilon=epsilon,Pi=Pi,denom=denom)

        # chose number of points to sample for r < r0 (does not
        # affect solution convergence).
        self.ivppoints = 1001

        # compute interpolations for w and w' right away to avoid
        # having to compute every time e.g. self.w(rs) is called.

        self.__interp_y,self.__interp_prime = self.__find_av_w()

        return

    def __ivpfun(self,r,y,xi):

        """
        RHS of y' = f(r,y) for IVP ODE to be solved, with y[0] = w, y[1] = w'.

        Parameters
        ----------

        r : array-like
            independent variable (distance between particles). MUST BE
            LESS THAN 2**(1./6.).
        y : array-like
            dependent variables with y[0] = w, y[1] = w'.
        xi: float
            xi value.

        Returns
        ------
        fun : np.array
            RHS of y' = f(r,y) (ODE at r) for r < 2**(1./6.).
        """


        return np.vstack((y[1],-(3/r -self.V_derivative(r) -xi)*y[1]
                          + (self.Pi/2 + self.V_derivative(r) + xi/r)*y[0]
                          + self.V_derivative(r)/(2*r)))

    def __bvpfun(self,r,y,xi):

        """
        RHS of y' = f(r,y) for BVP ODE to be solved, with y[0] = w, y[1] = w'.

        Parameters
        ----------

        r : array-like
            independent variable (distance between particles). MUST BE
            GREATER THAN 2**(1./6.).
        y : array-like
            dependent variables with y[0] = w, y[1] = w'.
        xi: float
            xi value.

        Returns
        ------
        fun : np.array
            RHS of y' = f(r,y) (ODE at r) for r > 2**(1./6.).
        """


        return np.vstack((y[1],-(3/r  -xi)*y[1] + (self.Pi/2  + xi/r)*y[0]))


    def __bvpfun_jac(self,r,y,xi):

        """
        Jacobian of f(r,y) where y' = f(r,y) for BVP ODE to be solved,
        with y[0] = w, y[1] = w'.

        Parameters
        ----------

        r : array-like
            independent variable (distance between particles). MUST BE
            GREATER THAN 2**(1./6.).
        y : array-like
            dependent variables with y[0] = w, y[1] = w'.
        xi: float
            xi value.

        Returns
        ------
        jac : np.array
            Jacobian of BVP ODE.
        """

        

        return np.array([[r*0,r*0+1],[self.Pi/2 + xi/r,-(3/r -xi)]])

    

    def __bc(self,ya,yb):

        """
        Boundary conditions at self.r0 and self.rinfty, the former
        being r0*w'(r0) + w(r0) + 1/self.denom = 0, the latter
        being w(rinfty) = 0.

        Parameters
        ----------

        ya : array-like
            dependent variables at r0.
        yb : array-like
            dependent variables at rinfty.

        Returns
        ------
        bc : np.array
            boundary conditions at the two endpoints.
        """


        return np.array([self.r0*ya[1]+ya[0]+1./self.denom,yb[0]])

    def __bc_jac(self,ya,yb):
        
        """
        The boundary condition Jacobians at self.r0 and self.rinfty.

        Parameters
        ----------

        ya : array-like
            dependent variables at r0.
        yb : array-like
            dependent variables at rinfty.


        Returns
        ------
        bc_jacs : list
            boundary condition Jacobians at the two endpoints.
        """

        
        return [np.array([[1,self.r0],[0,0]]),np.array([[0,0],[1,0]])]
    

    def __above_r0(self,xi):

        """
        Solve the BVP for r > 2**(1./6.) at a specified xi value.

        Parameters
        ----------

        xi: float
            xi value.

        Returns
        -------
        wr : array
            values of w on meshpoints for r >= 2**(1./6.)


        """

        f0 = lambda r,y : self.__bvpfun(r,y,xi)

        rs = np.linspace(self.r0,self.rinfty,num=self.bvpmesh,
                         endpoint=True)

        # use hard sphere values as guess.
        ys = np.array([self.hs.w(rs),self.hs.w_prime(rs)])
        
        f0_jac = lambda r,y : self.__bvpfun_jac(r,y,xi)


        res = solve_bvp(f0,self.__bc,rs,ys,fun_jac = f0_jac,bc_jac=self.__bc_jac)

        return res.sol(rs)


    def __below_r0(self,xi,y0):


        """
        Solve the IVP for r < 2**(1./6.) at a specified xi value.

        Parameters
        ----------

        xi: float
            xi value.
        y0 : array like
            array of initial values w(r0) and w'(r0).

        Returns
        -------
        wr : array
            values of w on ivppoints for r <= 2**(1./6.)


        """

        t_span = (self.r0,self.rlowlim)

        rs = np.linspace(self.r0,self.rlowlim,num=self.ivppoints,
                         endpoint=True)
        
        res = solve_ivp(self.__ivpfun,t_span,y0,args=(xi,),
                        t_eval = rs,
                        vectorized=True,dense_output=True)
        
        return res.y[:,::-1]


    def __find_av_w(self):

        """
        Find the average value of w(r) by sampling a num_rns
        randomly generated xi values from the rng.

        Returns
        -------
        interp_y : interp1d object
            interpolation of w in range rlowlim to rinfty.

        interp_prime : interp1d object
            interpolation of w' in range rlowlim to rinfty.


        """
        
        # generate a sample of xi values
        if self.noisetype == "uniform":
            xis = np.random.uniform(-0.5,0.5,size=self.num_rns)
            xis = xis*12*self.xivar
        elif self.noisetype == "gaussian":
            xis = np.random.normal(loc=0.0,scale=np.sqrt(self.xivar),
                                   size=self.num_rns)
        else:
            raise ValueError("noisetype variable must be either "
                             "'gaussian' or 'uniform'")
            
        self.xis = xis
        # these arrays will store the solutions w and w'
        av_uppers = np.zeros([2,self.bvpmesh],float)
        av_lowers = np.zeros([2,self.ivppoints],float)

        # calculate w and w' for each xi, then average
        for xi in xis:
            tmp = self.__above_r0(xi)
            av_uppers += tmp
            y0 = tmp[:,0]

            av_lowers += self.__below_r0(xi,y0)

        av_uppers /= self.num_rns
        av_lowers /= self.num_rns


        # generate x,y data for building interpolations via concatenation
        rlows  = np.linspace(self.rlowlim,self.r0,num=self.ivppoints,
                             endpoint=True)
        rupps = np.linspace(self.r0,self.rinfty,num=self.bvpmesh,
                            endpoint=True)

        rs = np.concatenate((rlows,rupps[1:]))
        ys = np.concatenate((av_lowers[0,:],av_uppers[0,1:]))
        yprimes = np.concatenate((av_lowers[1,:],av_uppers[1,1:]))


        return (interp1d(rs,ys,fill_value="extrapolate"),
                interp1d(rs,yprimes,fill_value="extrapolate"))


        
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

        
        r = np.asarray(r)

        if r.ndim == 2:

            out = meshODE(r,self.__interp_y)
        else:
            out = self.__interp_y(r)

        return out

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

        
        r = np.asarray(r)

        if r.ndim == 2:

            out = meshODE(r,self.__interp_prime)
        else:
            out = self.__interp_prime(r)

        return out
        
    

    

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

        

