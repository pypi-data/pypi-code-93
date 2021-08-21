import sys
sys.path.insert(0, '.')

import time
import numpy as np

import data_simulation_manager
from .data_simulation_manager import DataSimulationManager


class SyntheticSimulationManager(object):

    def __init__(self, save_folder='/Users/aki-nishimura/OneDrive/OHDSI/Data/anti_coagulant/'):
        self.dsm = DataSimulationManager(path_to_data=save_folder)

    def set_simulation_params(
            self, n, p, n_signal, corr_design=True, n_factor=100, seed=0
        ):
        self.n = n
        self.p
        beta_true = np.zeros(p)
        beta_true[:n_nonzero_coef] = 1
        y, X = data_simulation_manager.simulate_data(
            n, p, beta_true, link, seed, corr_design, n_factor
        )

    def run(self, n, p, n_signal, corr_design=True, n_factor=100, seed=0,
            n_full_bayes_iter=1000, n_empir_bayes_iter=5000):

        self.dsm.set_data_generation_info(
            n, p, n_signal, corr_design, n_factor=n_factor
        )
        regress_on = self.dsm.get_model_name(n_signal, corr_design, n_factor)
        print("Regressing on " + regress_on)

        # First run full Bayes to estimate global scale.
        beta_true = np.zeros(p)
        beta_true[:n_signal] = 1
        y, X = data_simulation_manager.simulate_data(
            n, p, beta_true, 'logit', seed, corr_design, n_factor
        )
        init = {
            'beta': np.concatenate(([0], beta_true)),
        }
        self.run_full_bayes_gibbs(y, X, init, n_full_bayes_iter)

        # Fix global scale, run cg and direct for the same number of iterations

        pass

    def run_full_bayes_gibbs(self, y, X, init, n_post_burnin):

        bridge = BayesBridge(y, X, model='logit', add_intercept=True)
        start_time = time.time()
        mcmc_output = bridge.gibbs(
            n_burnin, n_post_burnin, thin, reg_exponent, init, mvnorm_method,
            seed=seed, global_scale_update=global_shrinkage_update,
            params_to_save=['beta', 'global_scale', 'logp']
        )
        end_time = time.time()
        print("Posterior computation took {:3g} seconds.".format(
            end_time - start_time
        ))
        mcmc_output['_random_gen_state'] = None  # Make it picklable

        dsm.set_data_generation_info(n, p, n_nonzero_coef, corr_design,
                                     n_factor=n_factor)
        dsm.save_gibbs_output(mcmc_output)

