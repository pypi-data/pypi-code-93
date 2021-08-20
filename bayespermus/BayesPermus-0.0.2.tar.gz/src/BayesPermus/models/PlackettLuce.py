from .Base import Base

import numpy as np
import pystan

class PlackettLuceDirichlet(Base):
  def __init__(self, alpha, seed=1, num_chains=1, num_samples=2000):
    Base.__init__(self, stan_model='./stan/PlackettLuceDirichlet.stan', 
                  seed=seed, num_chains=num_chains, num_samples=num_samples)
    self.alpha = alpha    

  def get_model_data(self, permus):
    num_permus, num_algorithms = permus.shape
    model_data = {'num_permus': num_permus,
                  'num_algorithms': num_algorithms,
                  'permus': permus,
                  'alpha': self.alpha}
    return model_data

  def calculate_permu_prob(self, permu, params):
    num_algorithms = len(permu)
    ratings = params
    prob = 1

    for i in range(num_algorithms):
      denominator = np.sum([ratings[permu[j]] for j in range(i, num_algorithms)])
      prob *= ratings[permu[i]] / denominator

    return prob

class PlackettLuceGamma(Base):
  def __init__(self, alpha, beta, seed=1, num_chains=1, num_samples=2000):
    Base.__init__(self, stan_model='./stan/PlackettLuceGamma.stan', 
                  seed=seed, num_chains=num_chains, num_samples=num_samples)
    self.alpha = alpha
    self.beta = beta  

  def get_model_data(self, permus):
    num_permus, num_algorithms = permus.shape
    model_data = {'num_permus': num_permus,
                  'num_algorithms': num_algorithms,
                  'permus': permus,
                  'alpha': self.alpha,
                  'beta': self.beta}
    return model_data

  def calculate_permu_prob(self, permu, params):
    num_algorithms = len(permu)
    ratings = params
    prob = 1

    for i in range(num_algorithms):
      denominator = np.sum([ratings[permu[j]] for j in range(i, num_algorithms)])
      prob *= ratings[permu[i]] / denominator

    return prob
