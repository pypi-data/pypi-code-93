from __future__ import annotations

import abc
import os
import typing
from datetime import datetime
from typing import Any, Optional

import numpy as np
import torch
import tqdm

import power_cogs
from power_cogs.base.base import Base
from power_cogs.callbacks import after, before, callback
from power_cogs.callbacks.class_method_callback import ClassMethodCallback
from power_cogs.callbacks.save_checkpoint_callback import SaveCheckpointCallback
from power_cogs.cluster.local_cluster import LocalCluster
from power_cogs.config.config import class_config
from power_cogs.config.trainer_config import TrainerConfig
from power_cogs.utils.utils import makedirs


@class_config(TrainerConfig)
class BaseTorchTrainer(Base, metaclass=abc.ABCMeta):
    def __init__(self, config: Any, *args, **kwargs):
        self.config = config
        self.cluster_config = self.config.get("cluster_config")
        self._setup_defaults()
        self._setup()

    def _setup_defaults(self):
        if self.config.get("name", None) is None:
            self.name = self.__class__.__name__
            self.config["name"] = self.name
        self.name = self.config.get("name")
        self.current_iteration = 0
        self.checkpoint_interval = self.config.get("logging_config", {}).get(
            "checkpoint_interval", 100
        )
        self._setup_run_name()
        self.batch_size = self.config.get("batch_size")
        self.visualize = self.config.get("visualize")
        self.epochs = self.config.get("epochs")
        self.early_stoppage = self.config.get("early_stoppage")

    """
        Setup functions, ordering goes:
        setup -> setup_dataset -> setup_model -> setup_trainer
    """

    @before([ClassMethodCallback("setup")])
    @before([ClassMethodCallback("setup_cluster")])
    @before([ClassMethodCallback("setup_dataset")])
    @before([ClassMethodCallback("setup_model")])
    @before([ClassMethodCallback("setup_trainer")])
    def _setup(self):
        pass

    def setup(self):
        pass

    def setup_cluster(self):
        self.cluster = LocalCluster(self.cluster_config)

    def setup_trainer(self):
        pass

    def setup_model(self):
        pass

    def setup_dataset(self):
        pass

    """
        Train functions, ordering goes:
        pre_train -> train -> train_iter -> post_train
    """

    def pre_train(self):
        pass

    def post_train(self, *args, **kwargs):
        pass

    @before([ClassMethodCallback("_setup_run_name")])
    def _pre_train(self):
        self.pre_train()

    def _post_train(self, *args, **kwargs):
        self.post_train()

    def train_iter(self, batch_size=32, iteration=0, *args, **kwargs):
        raise NotImplementedError("train_iter not impemented!")

    @callback([SaveCheckpointCallback()])
    def _train_iter(self, batch_size: int = 32, epoch: int = 0):
        out = self.train_iter(batch_size, epoch)
        out["epoch"] = epoch
        self.current_iteration += 1
        return out

    @before([ClassMethodCallback("pre_train")])
    @after([ClassMethodCallback("post_train")])
    def train(
        self, batch_size=None, epochs=None, visualize=None
    ) -> typing.Dict[str, Any]:
        """Main training function, should call train_iter
        """
        _batch_size = self.config.get("batch_size", 1)
        _epochs = self.config.get("epochs", 1)
        if batch_size is None:
            batch_size = _batch_size
        if epochs is None:
            epochs = _epochs
        bar = tqdm.tqdm(np.arange(epochs))
        for i in bar:
            self.current_iteration = i
            output = self._train_iter(batch_size, i)
            metrics = output.get("metrics", {})
            description = "--".join(["{}:{}".format(k, metrics[k]) for k in metrics])
            bar.set_description(description)
        return metrics

    ### helpers ###
    def _setup_run_name(self):
        name = self.name
        self.base_path = self.config.get("logging_config", {}).get(
            "checkpoint_path", "checkpoints"
        )
        self.run_name = makedirs(
            "{}/{}_{}/".format(
                self.base_path, datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), name
            )
        )
        self.checkpoint_path = os.path.join(self.run_name, "checkpoints")

    def save_config(self, path: str) -> str:
        c = self._config_class.from_dict(self.config)
        p = power_cogs.config.save_config(c, path, self.name)
        return p

    def save(
        self,
        base_path: Optional[str] = None,
        step: Optional[int] = None,
        path_name: Optional[str] = None,
    ):
        self.current_iteration = 0
        checkpoint_path = self.checkpoint_path
        if base_path is not None:
            checkpoint_path = base_path
        if path_name is None:
            if step is None:
                step = self.current_iteration
            path = makedirs("{}/{}".format(checkpoint_path, step))
            torch_path = "{}/{}_iteration_{}.pt".format(path, self.name, step)
        else:
            path = makedirs("{}/{}".format(checkpoint_path, path_name))
            torch_path = "{}/{}.pt".format(path, self.name)
        checkpoint = {
            "model": self.model.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "scheduler": self.scheduler.state_dict(),
        }
        torch.save(checkpoint, torch_path)
        self.save_config(path)
        return path
