# Lint as: python3
  
'''
Policy class for computing action from weights and observation vector. 
Horia Mania --- hmania@berkeley.edu
Aurelia Guy
Benjamin Recht 
'''

"""Policy class for computing action from weights and observation vector.

It is a modified policy class from third_party/py/ARS/code/policies.py.
"""

import arspb.filter as ars_filter
import numpy as np
from six.moves import range
import arspb.env_utils


class Policy(object):
  """A policy class in reinforcement learning."""

  def __init__(self, policy_params, update_filter=True):
    """Initializes the policy.

    Args:
      policy_params: The parameters of a policy, which includes dimensionality
        of the observations, actions, the bounds of the actions, the parameters
        of the internal observation filter and the weights of the policy.
      update_filter: Whether to update the internal filters when the policy is
        used. This filter is used to normalize different observations into a
        similar range, which ease the learning.
    """
    self.ob_dim = policy_params["ob_dim"]
    self.ac_dim = policy_params["ac_dim"]
    self.action_low = policy_params["action_lower_bound"]
    self.action_high = policy_params["action_upper_bound"]
    self.weights = np.empty(0)
    # A filter for updating statistics of the observations and normalizing
    # inputs to the policies
    self.observation_filter = ars_filter.ars_filter(
        policy_params["ob_filter"], shape=self.ob_dim)

    self.update_filter = update_filter

  def update_weights(self, new_weights):
    self.weights[:] = new_weights[:]
    return

  def get_weights(self):
    return self.weights

  def get_observation_filter(self):
    return self.observation_filter

  def get_weights_plus_stats(self):
    mu, std = self.observation_filter.get_stats()
    aux = np.asarray([self.weights, mu, std])
    return aux

  def reset(self):
    pass

  def act(self, ob):
    raise NotImplementedError

  def copy(self):
    raise NotImplementedError


class LinearPolicy(Policy):
  """Linear policy class that computes action as <w, ob>."""

  def __init__(self, policy_params, update_filter=True):
    """Initializes the linear policy. See the base class for more details."""

    Policy.__init__(self, policy_params, update_filter=update_filter)
    if isinstance(self.ob_dim, dict):
      self.ob_dim = sum(self.ob_dim.values())
    self.weights = np.zeros(self.ac_dim * self.ob_dim, dtype=np.float64)
    
    if "weights" in policy_params:
      self.update_weights(policy_params["weights"])
    mean = policy_params.get("observation_filter_mean", None)
    std = policy_params.get("observation_filter_std", None)
    
    if policy_params["ob_filter"]=="MeanStdFilter" and update_filter==False:
      self.observation_filter.mean = mean
      self.observation_filter.std = std
      
  def act(self, ob):
    """Maps the observation to action.

    Args:
      ob: The observations in reinforcement learning.
    Returns:
      actions: The actions in reinforcement learning.
    """
    ob = self.observation_filter(ob, update=self.update_filter)
    if isinstance(ob, dict):
      ob = env_utils.flatten_observations(ob)
    matrix_weights = np.reshape(self.weights, (self.ac_dim, self.ob_dim))
    normalized_actions = np.clip(np.dot(matrix_weights, ob), -1.0, 1.0)
    actions = (
        normalized_actions * (self.action_high - self.action_low) / 2.0 +
        (self.action_low + self.action_high) / 2.0)
    return actions




#with bias
class LinearPolicy2(Policy):
  """Linear policy class that computes action as <w, ob>+bias."""

  def __init__(self, policy_params, update_filter=True):
    """Initializes the linear policy. See the base class for more details."""
    Policy.__init__(self, policy_params, update_filter=update_filter)
    if isinstance(self.ob_dim, dict):
      self.ob_dim = sum(self.ob_dim.values())
    self.weights = np.zeros(self.ac_dim * self.ob_dim+self.ac_dim, dtype=np.float64)
    
    if "weights" in policy_params:
      self.update_weights(policy_params["weights"])
    
    mean = policy_params.get("observation_filter_mean", None)
    std = policy_params.get("observation_filter_std", None)
    
    if policy_params["ob_filter"]=="MeanStdFilter" and update_filter==False:
      self.observation_filter.mean = mean
      self.observation_filter.std = std
      
  def act(self, ob):
    """Maps the observation to action.

    Args:
      ob: The observations in reinforcement learning.
    Returns:
      actions: The actions in reinforcement learning.
    """
    ob = self.observation_filter(ob, update=self.update_filter)
    if isinstance(ob, dict):
      ob = env_utils.flatten_observations(ob)
            
    num_weights = self.ac_dim*self.ob_dim
    
    matrix_weights = np.reshape(self.weights[:num_weights], (self.ac_dim, self.ob_dim))
    bias_weights = self.weights[num_weights:]
    normalized_actions = np.clip(np.dot(matrix_weights, ob)+bias_weights, -1.0, 1.0)
    actions = (
        normalized_actions * (self.action_high - self.action_low) / 2.0 +
        (self.action_low + self.action_high) / 2.0)
    return actions


class FullyConnectedNeuralNetworkPolicy(Policy):
  """Feed-forward fully connected neural network policy."""

  def __init__(self, policy_params, update_filter=True):
    """Initializes the linear policy. See the base class for more details."""

    Policy.__init__(self, policy_params, update_filter=update_filter)
    if isinstance(self.ob_dim, dict):
      self.ob_dim = sum(self.ob_dim.values())
    if "policy_network_size" in policy_params:
      self._hidden_layer_sizes = policy_params["policy_network_size"]
    else:
      self._hidden_layer_sizes = []
      layer_id = 0
      key = f"hidden_layer_size{layer_id}"
      while key in policy_params and policy_params[key] > 0:
        self._hidden_layer_sizes.append(policy_params[key])
        layer_id += 1
        key = f"hidden_layer_size{layer_id}"
    self._activation = policy_params.get("activation", "tanh")
    if self._activation == "tanh":
      self._activation = np.tanh
    elif self._activation == "clip":
      self._activation = lambda x: np.clip(x, -1.0, 1.0)
    self._layer_sizes = [self.ob_dim]
    self._layer_sizes.extend(self._hidden_layer_sizes)
    self._layer_sizes.append(self.ac_dim)
    self._layer_weight_start_idx = []
    self._layer_weight_end_idx = []
    num_weights = 0
    num_layers = len(self._layer_sizes)
    for ith_layer in range(num_layers - 1):
      self._layer_weight_start_idx.append(num_weights)
      num_weights += (
          self._layer_sizes[ith_layer] * self._layer_sizes[ith_layer + 1])
      self._layer_weight_end_idx.append(num_weights)
    self.weights = np.zeros(num_weights, dtype=np.float64)
    
    if "weights" in policy_params:
      self.update_weights(policy_params["weights"])
    mean = policy_params.get("observation_filter_mean", None)
    std = policy_params.get("observation_filter_std", None)
    n = policy_params.get("init_timesteps", None)
    
    if policy_params["ob_filter"]=="MeanStdFilter" and update_filter==False:
      self.observation_filter.mean = mean
      self.observation_filter.std = std
    

  def act(self, ob):
    """Maps the observation to action.

    Args:
      ob: The observations in reinforcement learning.
    Returns:
      actions: The actions in reinforcement learning.
    """
    ob = self.observation_filter(ob, update=self.update_filter)
    if isinstance(ob, dict):
      ob = env_utils.flatten_observations(ob)
    ith_layer_result = ob
    num_layers = len(self._layer_sizes)
    for ith_layer in range(num_layers - 1):
      mat_weight = np.reshape(
          self.weights[self._layer_weight_start_idx[ith_layer]:
                       self._layer_weight_end_idx[ith_layer]],
          (self._layer_sizes[ith_layer + 1], self._layer_sizes[ith_layer]))
      ith_layer_result = np.dot(mat_weight, ith_layer_result)
      ith_layer_result = self._activation(ith_layer_result)

    normalized_actions = ith_layer_result
    actions = (
        normalized_actions * (self.action_high - self.action_low) / 2.0 +
        (self.action_low + self.action_high) / 2.0)
    return actions

