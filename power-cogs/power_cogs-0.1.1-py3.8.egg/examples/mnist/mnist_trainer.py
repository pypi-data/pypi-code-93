import hydra.utils
import numpy as np
import torch
import torch.nn.functional as F

from power_cogs.base.torch.base_torch_trainer import BaseTorchTrainer
from power_cogs.callbacks import after, setup_callback
from power_cogs.callbacks.tensorboard_callback import TensorboardCallback

# internal
from power_cogs.config.config import class_config
from power_cogs.examples.mnist.config import MNISTTrainerConfig
from power_cogs.examples.mnist.mnist_dataset import MNISTDataset

# mnist
from power_cogs.examples.mnist.mnist_model import MNISTModel


@class_config(MNISTTrainerConfig)
class MNISTTrainer(BaseTorchTrainer):
    def __init__(self, config, *args, **kwargs):
        super(MNISTTrainer, self).__init__(config, *args, **kwargs)

    def setup(self):
        self.model_config = self.config.get("model_config")
        self.dataloader_config = self.config.get("dataloader_config")
        self.optimizer_config = self.config.get("optimizer_config")
        self.scheduler_config = self.config.get("scheduler_config")

    def setup_dataset(self):
        self.dataset = MNISTDataset()
        self.dataloader = hydra.utils.instantiate(
            self.dataloader_config, dataset=self.dataset
        )

    def setup_model(self):
        self.model = MNISTModel(self.model_config)

    def setup_trainer(self):
        self.optimizer = hydra.utils.instantiate(
            self.optimizer_config, params=self.model.parameters()
        )
        self.scheduler = hydra.utils.instantiate(
            self.scheduler_config, optimizer=self.optimizer
        )

    @after([TensorboardCallback()])
    def train_iter(self, batch_size: int = 32, epoch: int = 0):
        losses = []
        accs = []
        for batch_ndx, sample in enumerate(self.dataloader):
            self.optimizer.zero_grad()
            data = sample["data"].float()
            targets = sample["targets"]
            out = self.model(data)
            loss = F.cross_entropy(out, targets)
            loss.backward()
            self.optimizer.step()
            if self.scheduler is not None:
                self.scheduler.step()
            losses.append(loss.item())
            predicted = torch.argmax(out, dim=-1).numpy()
            targets = targets.numpy()
            acc = np.sum(predicted == targets) / targets.shape[0]
            accs.append(acc)
        acc = np.mean(accs)
        train_dict = {
            "out": None,
            "metrics": {
                "accuracy": acc,
                "loss": np.mean(losses),
                "min_loss": np.min(losses),
                "max_loss": np.max(losses),
                "mean_loss": np.mean(losses),
                "sum_loss": np.sum(losses),
                "median_loss": np.median(losses),
                "epoch": epoch,
            },
            "loss": np.mean(losses),
        }
        return train_dict

    @setup_callback([TensorboardCallback()])
    def pre_train(self):
        pass
