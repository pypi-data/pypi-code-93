import numpy as np
import scipy as sp
import pickle as pkl
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

import sys
sys.path.insert(0, '..')
from bayesbridge.mcmc_diagnostics import estimate_ess


class SimulationSummarizer(object):

    def __init__(self):
        pass

    def compute_std_difference(self, samples_1, samples_2, moment=1, n_burnin=0):
        # Compute the difference in the mean of the two samples and
        # estimate the Monte Carlo error of the difference.

        mean_1, ess_1, mc_var_1 = self.estimate_monte_carlo_error(samples_1 ** moment, n_burnin)
        mean_2, ess_2, mc_var_2 = self.estimate_monte_carlo_error(samples_2 ** moment, n_burnin)
        diff = mean_1 - mean_2
        mc_var = mc_var_1 + mc_var_2
        std_diff = diff / np.sqrt(mc_var)
        return mean_1, mean_2, ess_1, ess_2, std_diff

    @staticmethod
    def estimate_monte_carlo_error(samples, n_burnin=0):
        post_burnin = samples[:, n_burnin:]
        mean = np.mean(post_burnin, 1)
        ess = estimate_ess(post_burnin, axis=-1)
        mc_var = np.var(post_burnin, axis=1) / ess
        return mean, ess, mc_var

    def plot_refline(self, x, y, label=None):
        plt.plot(
            [x.min(), x.max()],
            [y.min(), y.max()],
            '--',
            color='tab:green',
            label=label
        )

    def plot_posterior_summary_comparison(self, direct_mean, cg_mean, moment=1, label="ref line: x = y"):
        subset_ind = (direct_mean > - float('inf')) # Don't remember why I did this
        self.plot_refline(
            direct_mean[subset_ind],
            cg_mean[subset_ind],
            label=label
        )
        plt.plot(
            direct_mean[subset_ind],
            cg_mean[subset_ind],
            'o', fillstyle='none', ms=12,
            rasterized=True
        )
        legend = None
        if label is not None:
            legend = plt.legend(loc=[.26, .08], frameon=False)
        x_estimand, y_estimand = self.get_estimand_str(moment)
        plt.xlabel(r'${:s}$'.format(x_estimand))
        plt.ylabel(r'${:s}$'.format(y_estimand))
        plt.gca().set_aspect('equal', 'box')
        return legend

    def plot_std_diff_hist(self, std_diff, moment=1):

        width = max(np.abs(np.min(std_diff)), np.max(std_diff))
        bins = np.linspace(-width, width, 51)

        plt.hist(std_diff, bins=bins, density=True,
                 label='observed')
        x = np.linspace(-width, width, 101)
        plt.plot(x, sp.stats.norm.pdf(x), 'C2-',
                 label='null')
        bench_estimand, cg_estimand = self.get_estimand_str(moment, hatted=True)
        plt.xlabel(
            r'$\left( {:s} - {:s} \right) '.format(cg_estimand, bench_estimand)
            + '\, / \, \hat{\sigma}_j$'
        )
        plt.yticks([])
        legend = plt.legend(loc='upper right', frameon=False)
        # plt.xlim([-4.2, 4.2])
        return legend

    def plot_ess_comparion(self, direct_ess, cg_ess, moment=1, label=None):

        plt.loglog(
            direct_ess, cg_ess, 'o',
            alpha=.25, rasterized=True
        )
        self.plot_refline(direct_ess, cg_ess, label)

        ticks = [500, 1000, 2000]
        tick_labels = [r' $5 \! \times \! 10^2$', r'$10^3$', r' $2 \! \times \! 10^3$']
        ax = plt.gca()
        ax.xaxis.set_major_formatter(NullFormatter())
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.yaxis.set_major_formatter(NullFormatter())
        ax.yaxis.set_minor_formatter(NullFormatter())
            # Deal with bug https://github.com/matplotlib/matplotlib/issues/8027/
        plt.xticks(ticks, tick_labels)
        plt.yticks(ticks, tick_labels)

        x_estimand, y_estimand = self.get_estimand_str(moment)
        x_label = r'ESS of ${:s}$'.format(x_estimand)
        y_label = r'ESS of ${:s}$'.format(y_estimand)
        plt.xlabel(x_label)
        plt.ylabel(y_label)

        plt.gca().set_aspect('equal', 'box')

    def get_estimand_str(self, moment, hatted=False):
        if hatted:
            coef_symbol = r'\hat{\beta}'
        else:
            coef_symbol = r'\beta'
        x_estimand = coef_symbol + r'_{{\rm bench}, j}'
        y_estimand = coef_symbol + r'_{{\rm cg}, j}'
        if moment == 2:
            x_estimand = r'{:s}^{:d}'.format(x_estimand, moment)
            y_estimand = r'{:s}^{:d}'.format(y_estimand, moment)
        return x_estimand, y_estimand

    def get_linalg_cost(self, n_obs, n_pred, n_thread):

        if n_thread == 1:
            matvec_cost = [.0236, .0933, .414]
            matmat_cost = [5.57, 43.5, 345]
            chol_cost = [0.932, 6.95, 52.1]
        elif n_thread == 4:
            matvec_cost = [.0205, .0822, .334]
            matmat_cost = [1.88, 15.1, 113]
            chol_cost = [0.422, 2.87, 19.9]
        else:
            raise ValueError()

        index = {
            (12500, 5000): 0,
            (25000, 10000): 1,
            (50000, 20000): 2,
        }[(n_obs, n_pred)]

        return matvec_cost[index], matmat_cost[index], chol_cost[index]

