from __future__ import annotations

import os
import time
import typing
from typing import Callable, Optional

import attr
import gym
import numpy as np
import ray
import torch
from torch.distributions.categorical import Categorical

# internal
from power_cogs.cluster.execution import Execution


@attr.s(repr=False)
class RolloutExecution(Execution):

    env: Optional[gym.Env] = attr.ib(default=None)
    env_name: str = attr.ib(default="LunarLander-v2")
    max_env_steps: int = attr.ib(default=10 ** 10)
    gamma: float = attr.ib(default=0.99)
    discount_rewards: bool = attr.ib(default=True)
    normalize_rewards: bool = attr.ib(default=True)
    random_policy: bool = attr.ib(default=False)
    stop_criteria: Optional[Callable] = attr.ib(default=None)
    preprocess_observation_func: Optional[Callable] = attr.ib(default=None)

    def __attrs_post_init__(self):
        # Tell numpy to only use one core. If we don't do this, each actor may
        # try to use all of the cores and the resulting contention may result
        # in no speedup over the serial version. Note that if numpy is using
        # OpenBLAS, then you need to set OPENBLAS_NUM_THREADS=1, and you
        # probably need to do it from the command line (so it happens before
        # numpy is imported).
        os.environ["MKL_NUM_THREADS"] = "1"
        if self.env is None:
            self.env = gym.make(self.env_name)
        if self.preprocess_observation_func is None:
            self.preprocess_observation_func = self.preprocess_torch

    def preprocess_torch(self, env, observation):
        return observation

    def discount(self, r) -> np.array:
        """Compute discounted reward from a vector of rewards."""
        discounted_r = np.zeros_like(r)
        running_add = 0
        for t in reversed(range(0, r.size)):
            # Reset the sum, since this was a game boundary (pong specific!).
            if r[t] != 0:
                running_add = 0
            running_add = running_add * self.gamma + r[t]
            discounted_r[t] = running_add
        return discounted_r

    def normalize(self, r):
        r = r - np.mean(r)
        r = r / np.std(r) + 1e-7
        return r

    def rollout(
        self,
        model: torch.nn.Module = None,
        render: bool = False,
        random_policy: Optional[bool] = None,
        close: bool = False,
    ) -> typing.Tuple[np.array, np.array, np.array]:
        """Evaluates  env and model until the env returns "Done".
        Returns:
            xs: A list of observations
            hs: A list of model hidden states per observation
            dlogps: A list of gradients
            drs: A list of rewards.
        """
        if random_policy is None:
            random_policy = self.random_policy
        # Reset the game.
        observation = self.env.reset()
        observations, actions, rewards, dones = [], [], [], []
        done = False
        i = 0
        while not done:
            if render:
                self.env.render()
                time.sleep(0.01)
            observation = self.preprocess_observation_func(self.env, observation)
            if random_policy or model is None:
                action = self.env.action_space.sample()
            else:
                logits = model.forward_policy(observation)
                dist = Categorical(logits=logits.squeeze())
                action = dist.sample().item()

            actions.append(action)
            observations.append(observation.cpu().detach().numpy())

            observation, reward, done, info = self.env.step(action)
            rewards.append(reward)
            dones.append(float(done))
            i += 1
            if i >= self.max_env_steps:
                done = True
            elif self.stop_criteria is not None:
                if self.stop_criteria(observation, reward, done, info):
                    done = True

        observations = np.array(observations)
        actions = np.array(actions)
        rewards = np.array(rewards)
        dones = np.array(dones)

        if close:
            self.env.close()

        if self.discount_rewards:
            rewards = self.discount(rewards)

        if getattr(self.env.action_space, "n"):
            zeros = np.zeros((actions.shape[0], self.env.action_space.n))
            for i in range(zeros.shape[0]):
                zeros[i][actions[i]] = 1
            categorical_actions = zeros

            return {
                "observations": observations,
                "actions": actions,
                "categorical_actions": categorical_actions,
                "rewards": rewards,
                "dones": dones,
            }
        return {
            "observations": observations,
            "actions": actions,
            "rewards": rewards,
            "dones": dones,
        }

    def execute(self, *args, **kwargs):
        return self.rollout(*args, **kwargs)

    @classmethod
    def create(cls, *args, **kwargs) -> RolloutExecution:
        """Return an ray actor class
        Returns:
            Execution
        """
        return ray.remote(cls).remote(*args, **kwargs)
