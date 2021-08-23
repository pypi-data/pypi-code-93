from typing import Any

import gym
import numpy as np
import torch
from gym.spaces import Discrete

# internal
from power_cogs.base import Base
from power_cogs.cluster.cluster import Cluster
from power_cogs.cluster.execution import RolloutExecution
from power_cogs.config.config import class_config
from power_cogs.examples.reinforce.config import RolloutDatasetConfig


@class_config(RolloutDatasetConfig)
class RolloutDataset(Base):
    def __init__(self, config={}):
        self.config = config
        self.env_name = config.get("env_name")
        self.max_env_steps = config.get("max_env_steps")
        self.gamma = config.get("gamma")
        self.discount_rewards = config.get("discount_rewards")
        self.normalize_rewards = config.get("normalize_rewards")
        self.random_policy = config.get("random_policy")
        self.num_rollouts = config.get("num_rollouts")
        self.num_workers = config.get("num_workers")

    def get_env_dims(self):
        env = gym.make(self.env_name)
        # env_type = getattr(env, "env_type", "default")
        env = gym.make(self.env_name)
        state_shape = env.observation_space.shape
        if isinstance(env.action_space, Discrete):
            action_shape = [env.action_space.n]
        else:
            action_shape = env.action_space.shape
        return state_shape, action_shape

    def preprocess_torch(self, env, observation):
        return torch.from_numpy(observation).float()

    def stop_criteria(self, observation, reward, done, info):
        return False

    def discount_reward(self, reward_arr):
        dr = [0] * (len(reward_arr) + 1)
        for i in range(len(reward_arr) - 1, -1, -1):
            dr[i] = reward_arr[i] + self.gamma * dr[i + 1]
        dr = np.array(dr[: len(reward_arr)])
        return dr

    def get_rollouts(self, cluster: Cluster, model: Any = None):
        rollout_workers = [
            cluster.create_execution(
                RolloutExecution,
                env_name=self.env_name,
                max_env_steps=self.max_env_steps,
                gamma=self.gamma,
                discount_rewards=self.discount_rewards,
                normalize_rewards=self.normalize_rewards,
                random_policy=self.random_policy,
                stop_criteria=self.stop_criteria,
                preprocess_observation_func=self.preprocess_torch,
            )
            for i in range(self.num_workers)
        ]
        # if isinstance(self.cluster, RayCluster):
        #     model_id = self.cluster.put(self.model, name="model")["model"]
        #     rollout_args = [
        #         {"model": model_id, "render": False} for i in range(self.num_rollouts)
        #     ]
        #     return [self.cluster.execute_list(self.rollout_workers, rollout_args)]
        rollout_args = [
            {"model": model, "render": False} for i in range(self.num_rollouts)
        ]
        return cluster.execute_list(rollout_workers, rollout_args)
