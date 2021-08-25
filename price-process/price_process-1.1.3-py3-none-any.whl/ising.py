from .helpers import *
from numpy.random import randint, rand
from tqdm import tqdm


class MCising:
    def __init__(self, beta,lag, size, N=10, J=1, h=2, show_progress=True, verbose=False):
        self.state = 2 * randint(2, size=(N, N)) - 1
        self.n = len(self.state)
        self.N, self.size, self.J, self.h, self.beta, self.lag = N, size, J, h, beta, lag
        self.n_samples = size[0]
        self.n_samples_ = size[1]
        self.show_progress, self.verbose = show_progress, verbose
        self.mag = self.state.sum()
        self.mag_mat = np.zeros(self.n_samples*self.n_samples_)
        self.pre_process = None

    def nn(self, i, j):
        return self.state[(i + 1) % self.N, j] + self.state[(i - 1) % self.N, j] + self.state[i, (j + 1) % self.N] + \
               self.state[i, (j - 1) % self.N]

    def step(self):
        self.mag = self.state.sum()
        for i in range(0, self.n):
            for j in range(0, self.n):
                x, y = randint(0, self.N), randint(0, self.N)
                dE = 2 * self.J * self.state[x, y] * self.nn(x, y) + 2 * self.state[x, y] * self.h * abs(self.mag) / (
                            self.N ** 2 * self.n_samples)
                if dE < 0 or rand() < np.exp(-self.beta * dE):
                    self.state[x, y] *= -1
        self.mag = self.state.sum()

    def run(self, n_therm=200):
        if self.verbose:
            print("Running MC on " + str(self.N) + "x" + str(self.N) + " square lattice")
            print("Inverse temperature: ", self.beta)
            print("Number of MC samples: ", self.n_samples)
            print("Thermalization steps: ", n_therm)
            print("J: ", self.J, "/kB")
            print("h: ", self.h, "/kB")
        mag_ = 0
        for mc_idx in tqdm(range(0, self.size[0]*self.size[1]), disable=not self.show_progress):
            if mc_idx == 0:
                for therm_idx in range(0, n_therm):
                    self.step()
            self.step()
            mag_ += self.mag
            self.mag_mat[mc_idx] = self.mag
            if not mc_idx%self.size[0]:
                for therm_idx in range(0, n_therm):
                    self.step()
        self.pre_process = self.mag_mat.reshape(self.size)

    def get_returns_mat(self, lag):
        self.returns_mat = (self.mag_mat[:, :] - shift(self.mag_mat[:, :], -lag))
        return self.returns_mat

    @property
    def price(self):
        """Interface, do not use independently"""
        self.run()
        return np.exp(moving_average(self.pre_process, self.lag))

# plt.plot(MCising(0.05, 500, [1000, 10]).price)
# plt.show()
