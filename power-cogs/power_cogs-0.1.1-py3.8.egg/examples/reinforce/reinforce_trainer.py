import hydra.utils
import numpy as np
import torch
from torch.distributions.categorical import Categorical

from power_cogs.base.torch.base_torch_trainer import BaseTorchTrainer
from power_cogs.callbacks import after, setup_callback
from power_cogs.callbacks.tensorboard_callback import TensorboardCallback

# internal
from power_cogs.config.config import class_config
from power_cogs.examples.reinforce.config import ReinforceTrainerConfig

# reinforce
from power_cogs.examples.reinforce.policy_mlp_model import PolicyMLPModel
from power_cogs.examples.reinforce.rollout_dataset import RolloutDataset


@class_config(ReinforceTrainerConfig)
class ReinforceTrainer(BaseTorchTrainer):
    def __init__(self, config, *args, **kwargs):
        super(ReinforceTrainer, self).__init__(config, *args, **kwargs)

    def setup(self):
        self.dataset_config = self.config.get("dataset_config")
        self.model_config = self.config.get("model_config")
        self.optimizer_config = self.config.get("optimizer_config")
        self.scheduler_config = self.config.get("scheduler_config")

        self.dataset = RolloutDataset(self.dataset_config)
        self.state_shape, self.action_shape = self.dataset.get_env_dims()
        self.model_config["input_dims"] = self.state_shape[0]
        self.model_config["output_dims"] = self.action_shape[0]
        self.gamma = self.dataset.gamma

    def setup_model(self):
        self.model = PolicyMLPModel(self.model_config)

    def setup_trainer(self):
        self.optimizer = hydra.utils.instantiate(
            self.optimizer_config, params=self.model.parameters()
        )
        self.scheduler = hydra.utils.instantiate(
            self.scheduler_config, optimizer=self.optimizer
        )

    def discount_reward(self, reward_arr):
        dr = [0] * (len(reward_arr) + 1)
        for i in range(len(reward_arr) - 1, -1, -1):
            dr[i] = reward_arr[i] + self.gamma * dr[i + 1]
        dr = np.array(dr[: len(reward_arr)])
        return dr

    @after([TensorboardCallback()])
    def train_iter(self, batch_size: int = 32, epoch: int = 0):
        losses = []
        rollouts = self.dataset.get_rollouts(self.cluster, self.model)
        total_rewards = []
        for rollout in rollouts:
            rollout_sample = rollout[0]
            observations = rollout_sample["observations"]
            actions = rollout_sample["actions"]
            rewards = rollout_sample["rewards"]

            rewards = np.squeeze(rewards)
            total_rewards.append(np.sum(rewards))
            if self.dataset.discount_rewards:
                rewards = self.discount_reward(rewards)
            if self.dataset.normalize_rewards:
                rewards = rewards - np.mean(rewards)
                rewards = rewards / np.std(rewards) + 1e-5
            observations = torch.from_numpy(observations).float()
            actions = torch.from_numpy(actions).float()
            rewards = torch.from_numpy(rewards).float()

            self.optimizer.zero_grad()

            out = self.model.forward_policy(observations)
            dist = Categorical(logits=out)
            log_probs = -1 * dist.log_prob(actions)

            loss = (1 / self.dataset.num_rollouts) * torch.sum(rewards * log_probs)
            loss.backward()
            self.optimizer.step()
            self.scheduler.step()
            losses.append(loss.item())

        grad_dict = {}
        for n, W in self.model.named_parameters():
            if W.grad is not None:
                grad_dict["{}_grad".format(n)] = float(torch.sum(W.grad).item())
        train_dict = {
            "out": None,
            "metrics": {
                "average_summed_rewards": np.mean(total_rewards),
                "max_summed_rewards": np.max(total_rewards),
                "loss": np.mean(losses),
                "max_loss": np.max(losses),
                "sum_loss": np.sum(losses),
                "epoch": epoch,
                **grad_dict,
            },
            "loss": np.mean(losses),
        }
        return train_dict

    @setup_callback([TensorboardCallback()])
    def pre_train(self):
        pass
