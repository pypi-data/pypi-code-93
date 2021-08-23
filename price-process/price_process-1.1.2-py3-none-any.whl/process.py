from .ising import *


class Process():

    def __init__(self, size, initial=0, T=1):
        """

        Parameters
        ----------
        size :  int or int pair
                tuple or array of the form `[n_steps, n_samples]`
        initial :   float, optional
                    initial value of process
        T : float, optional
            terminal value of time sequence: :math:`t_{nsteps}=T`. (:math`t_0=0` wlog)
        """
        if hasattr(size, "__len__"):
            if len(size) != 2:
                raise ValueError(f"size of random matrix to be generated must be 2, not {len(size)}")
            else:
                self.n_steps = size[0]
                self.n_samples = size[1]
        else:
            self.n_steps = size
            self.n_samples = 1
        self.size = size
        self.initial = initial
        self.T = T
        self.t = np.linspace(0, self.T, self.n_steps)
        self.process = None
        self.log_process = None

    def to_geometric(self, drift, vol):
        """
        Maps a log_process to its exponential: :math:`S_t\mapsto e^{\mu t+\sigma S_t}` with :math:`\mu` and :math:`\sigma`
        being the drift and (percent) volatility parameters.

        Parameters
        ----------
        drift : float
                any real number
        vol :   float
                any positve real number, typically close to <1 and close to 0.

        Returns
        -------
        self
            Process
        """
        self.log_process = self.process
        self.process = normalize(np.exp(self.log_process*vol+(drift-0.5*vol**2)))
        return self

    def plot(self, title=None, figsize=(10, 5)):
        """
        Plots `self.process`

        Parameters
        ----------
        title : str or None, optional
        figsize:    pair of ints, optional

        Returns
        -------
        matplotlib Figure
            Plot of process
        """
        plt.figure(figsize=figsize)
        plt.plot(self.t, self.process)
        plt.xlabel(r'$t$')
        plt.title(title)
        plt.show()

    def resample(self, resampling_proc):
        """
        Resamples `self.process` with another stochastic process.

        Parameters
        ----------
        resampling_proc : ndarray of same shape as `self.process`

        Returns
        -------
        self
            Process
        """
        if resampling_proc.shape != self.process.shape:
            raise IndexError(f"The indices of the resampling process are out of bounds for original shape of {self.process.shape}")
        idx = self.T*normalize(resampling_proc)*(self.n_steps-1)
        self.process = normalize(self.process[idx.astype("int")][:, 0, :])
        return self

    def returns(self, idx=0, order=1):
        """
        Differences `self.process` to a given order at given sample index.

        Parameters
        ----------
        idx :   int
                indexes the sample axis
        order : int or float
                positive integer or real indicating order of differencing. Fast fractional differencing not implemented

        Returns
        -------
        ndarray
            normalized returns
        """
        return normalize(integer_difference(self.process[:, idx], self.t, n=order))


class Gaussian(Process):
    """
    Gaussian process subclass
    """
    def __init__(self,size, mu=0, std=1, initial=0, T=1):
        """

        Parameters
        ----------
        size :  int or int pair
                tuple or array of the form `[n_steps, n_samples]`
        mu :    float, optional
                mean of normal distribution
        std :   float, optional
                standard deviation of normal distribution
        initial :   float, optional
                    initial value of process
        T : float, optional
            terminal value of time sequence: :math:`t_{nsteps}=T`. (:math`t_0=0` wlog)
        """
        super().__init__(size, initial=initial, T=T)
        self.mu, self.std = mu, std
        if self.mu != 0 or self.std != 1:
            raise Warning("Using non-standard underlying process")
        self.rvs = norm.rvs(mu, std, self.size)
        self.process = normalize(np.cumsum(self.rvs, axis=0))


class Levy(Process):
    """
    Levy-stable process subclass
    """
    def __init__(self, alpha, beta, size, mu=0, std=1, initial=0, T=1):
        """

        Parameters
        ----------
        size :  int or int pair
                tuple or array of the form `[n_steps, n_samples]`
        alpha :    float
                stability parameter, :math:`0<\alpha<1`
        beta :   float
                skewness parameter
        initial :   float, optional
                    initial value of process
        T : float, optional
            terminal value of time sequence: :math:`t_{nsteps}=T`. (:math`t_0=0` wlog)
        """
        super().__init__(size, initial=initial, T=T)
        if 0 < alpha <= 2 and -1 <= beta <= 1:
            self.alpha, self.beta = alpha, beta
        else:
            raise ValueError("Parameter bounds: 0<alpha<=2, -1<=beta<=1")

        self.mu, self.std = mu, std
        self.rvs = levy_stable.rvs(self.alpha, self.beta, size=self.size, loc=mu, scale=std**2)
        if self.mu != 0 or self.std != 1:
            raise Warning("Using non-standard underlying process")
        self.process = normalize(np.cumsum(self.rvs, axis=0))

    def plot_pdf(self, bounds=(-7, 7), n=200):
        """
        The Levy process can lead to dramatically different stochastic dynamics so it's helpful to keep a comparison
        to the standard normal distribution in mind when tuning parameters.

        Parameters
        ----------
        bounds :    pair of ints, optional
                    bounds on x-axis
        n : int, optional
            number of steps in x-axis

        Returns
        -------
        matplotlib Figure
            plot of the Levy pdf compared to the standard normal pdf
        """
        x = np.linspace(*bounds, n)
        plt.plot(x, normalize(levy_stable.pdf(x, self.alpha, self.beta, loc=self.mu, scale=self.std)), label=f"Levy ({self.alpha}, {self.beta})")
        plt.plot(x, normalize(norm.pdf(x, loc=self.mu, scale=self.std*np.sqrt(2))), '--', label="Normal")
        plt.legend()
        plt.show()


class Ising(Process):
    """
    Price process derived from universal Ising dynamics
    """
    def __init__(self, vol, window, size, initial=0, T=1, N=10, J=1, h=2, show_progress=True, verbose=False):
        """

        Parameters
        ----------
        vol :   float
                inverse temperature, stand-in for volatility. Optimal values depend on system size. For the default settings, 0.01-0.05 is ideal. If it is too high,
                the model will freeze out.
        window :    int
                    coarse-graining parameter used in the exponential moving average. Ballpark of `size[0]/2` is ideal
        size :  int or int pair
                tuple or array of the form `[n_steps, n_samples]`
        initial :   float, optional
                    initial value of process
        T : float, optional
            terminal value of time sequence: :math:`t_{nsteps}=T`. (:math`t_0=0` wlog)
        N : int, optional
            generates [N,N] lattice
        J : positive float, optional
            controls scale of herding behavior
        h : positive float, optional
            controls scale of contrarian behavior
        show_progress : bool, optional
        verbose : bool, optional
        """
        super().__init__(size, initial=initial, T=T)
        self.process = normalize(MCising(vol, window, size, N=N, J=J, h=h, show_progress=True, verbose=False).price)
        self.t = np.linspace(0, self.T, len(self.process))
        self.size = self.process.shape

