from .Base import Base

import numpy as np
import pystan

class BradleyTerry(Base):
  def __init__(self, alpha, seed=1, num_chains=1, num_samples=2000):
    Base.__init__(self, stan_model='./stan/BradleyTerry.stan', 
                  seed=seed, num_chains=num_chains, num_samples=num_samples)
    self.alpha = alpha

  def get_model_data(self, permus):
    num_permus, num_algorithms = permus.shape

    model_data = {'num_permus': num_permus,
                  'num_algorithms': num_algorithms,
                  'permus': permus,
                  'alpha': self.alpha}
    return model_data

  def get_samples(self, data):
    result = [(ratings, constant) for ratings, constant in zip(data['ratings'], data['constant'])]
    return result

  def calculate_permu_prob(self, permu, params):
    num_algorithms = len(permu)
    ratings, constant = params
    prob = 1

    for i in range(num_algorithms):
      prob *= ratings[permu[i]] ** (num_algorithms - i - 1)
  
    return prob / constant

  

