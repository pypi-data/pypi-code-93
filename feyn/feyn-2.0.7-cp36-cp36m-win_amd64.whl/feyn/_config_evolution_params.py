"""Redefine here some pruning parameters related to model half life and strength.

Half life formula:

model_age = A0 * exp(-cnt / (density / (n * tau))) + 1,

where by default A0 = 200, n = 20, and tau = 0.693.
"""


_HalfLife_params = {}
