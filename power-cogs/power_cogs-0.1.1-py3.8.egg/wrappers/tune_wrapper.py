import copy
import os
from collections.abc import Iterable
from multiprocessing import Process, Queue
from numbers import Number
from typing import Any, Dict, List, Tuple

import attr
import numpy as np
import omegaconf
import wandb
from omegaconf import OmegaConf
from ray import tune
from ray.tune.integration.mlflow import MLflowLoggerCallback
from ray.tune.integration.wandb import WandbLoggerCallback
from ray.tune.trial import Trial
from ray.tune.utils import flatten_dict

from power_cogs.base.torch.base_torch_trainer import BaseTorchTrainer

_WANDB_QUEUE_END = (None,)
_VALID_TYPES = (Number, wandb.data_types.Video)
_VALID_ITERABLE_TYPES = wandb.data_types.Video


def _is_allowed_type(obj):
    """Return True if type is allowed for logging to wandb"""
    if isinstance(obj, np.ndarray) and obj.size == 1:
        return isinstance(obj.item(), Number)
    if isinstance(obj, Iterable) and len(obj) > 0:
        return isinstance(obj[0], _VALID_ITERABLE_TYPES)
    return isinstance(obj, _VALID_TYPES)


class _WandbLoggingProcess(Process):
    """
    We need a `multiprocessing.Process` to allow multiple concurrent
    wandb logging instances locally.
    """

    def __init__(
        self, queue: Queue, exclude: List[str], to_config: List[str], *args, **kwargs
    ):
        super(_WandbLoggingProcess, self).__init__()
        self.queue = queue
        self._exclude = set(exclude)
        self._to_config = set(to_config)
        self.args = args
        self.kwargs = kwargs

    def run(self):
        wandb.init(*self.args, **self.kwargs)
        while True:
            result = self.queue.get()
            if result == _WANDB_QUEUE_END:
                break
            wandb_artifact_checkpoint_dir = result.get(
                "wandb_artifact_checkpoint_dir", None
            )
            if wandb_artifact_checkpoint_dir is not None:
                wandb_artifact_checkpoint_name = result.get(
                    "wandb_artifact_checkpoint_name", None
                )
                artifact = wandb.Artifact(
                    wandb_artifact_checkpoint_name, type="raw_data"
                )
                for content in os.listdir(wandb_artifact_checkpoint_dir):
                    d = os.path.join(wandb_artifact_checkpoint_dir, content)
                    try:
                        if os.path.isdir(d):
                            artifact.add_dir(d)
                        else:
                            artifact.add_file(d)
                    except Exception:
                        pass
                wandb.log_artifact(artifact)
            else:
                log, config_update = self._handle_result(result)
                wandb.config.update(config_update, allow_val_change=True)
                wandb.log(log)
        wandb.join()

    def _handle_result(self, result: Dict) -> Tuple[Dict, Dict]:
        config_update = result.get("config", {}).copy()
        log = {}
        flat_result = flatten_dict(result, delimiter="/")

        for k, v in flat_result.items():
            if any(k.startswith(item + "/") or k == item for item in self._to_config):
                config_update[k] = v
            elif any(k.startswith(item + "/") or k == item for item in self._exclude):
                continue
            elif not _is_allowed_type(v):
                continue
            else:
                log[k] = v

        config_update.pop("callbacks", None)  # Remove callbacks
        return log, config_update


class CustomWandbLoggerCallback(WandbLoggerCallback):
    _logger_process_cls = _WandbLoggingProcess

    def __init__(self, *args, **kwargs):
        super(CustomWandbLoggerCallback, self).__init__(*args, **kwargs)

    def on_trial_save(self, iteration: int, trials: List[Trial], trial: Trial, **info):
        """Called after receiving a checkpoint from a trial.
        Arguments:
            iteration (int): Number of iterations of the tuning loop.
            trials (List[Trial]): List of trials.
            trial (Trial): Trial that just saved a checkpoint.
            **info: Kwargs dict for forward compatibility.
        """
        result = {
            "wandb_artifact_checkpoint_dir": trial.logdir,
            "wandb_artifact_checkpoint_name": trial.trainable_name
            + "-"
            + trial.trial_id,
        }
        try:
            self._trial_queues[trial].put(result)
        except Exception:
            pass


class CustomMLflowLoggerCallback(MLflowLoggerCallback):
    def __init__(self, *args, **kwargs):
        super(CustomMLflowLoggerCallback, self).__init__(*args, **kwargs)

    def on_trial_save(self, iteration: int, trials: List[Trial], trial: Trial, **info):
        """Called after receiving a checkpoint from a trial.
        Arguments:
            iteration (int): Number of iterations of the tuning loop.
            trials (List[Trial]): List of trials.
            trial (Trial): Trial that just saved a checkpoint.
            **info: Kwargs dict for forward compatibility.
        """
        run_id = self._trial_runs[trial]

        # Log the artifact if set_artifact is set to True.
        self.client.log_artifacts(run_id, local_dir=trial.logdir)


class TuneTrainer(tune.Trainable):
    def setup(self, config):
        self.trainer_class = config.get("trainer_class")
        self.trainer_config = config.get("trainer_config")
        self.trainer = self.trainer_class(self.trainer_config)
        self.trainer.pre_train()

    def step(self):
        out = self.trainer.train_iter(
            self.trainer.batch_size, self.trainer.current_iteration
        )
        self.trainer.current_iteration += 1
        return out["metrics"]

    def save_checkpoint(self, tmp_checkpoint_dir):
        return self.trainer.save(tmp_checkpoint_dir)

    def load_checkpoint(self, tmp_checkpoint_dir):
        self.trainer.load(
            os.path.join(tmp_checkpoint_dir, "{}.pt".format(self.trainer.name))
        )


def create_stopper(config):
    epochs = config.get("epochs", 1000) + 1
    loss_threshold: float = -float("inf")
    if config.get("early_stoppage"):
        loss_threshold = config.get("loss_threshold", -float("inf"))

    def stopper(trial_id, result):
        if result["training_iteration"] >= epochs:
            return True
        return result["loss"] < loss_threshold

    return stopper


@attr.s
class TuneWrapper:

    trainer: BaseTorchTrainer = attr.ib()
    config: Any = attr.ib(init=False, default={})

    def __attrs_post_init__(self):
        self.config = self.trainer.config
        if isinstance(self.config, omegaconf.dictconfig.DictConfig):
            self.config = OmegaConf.to_container(self.config)

    def tune(self):
        self.trainer.current_iteration = 0
        mlflow_config = self.config["logging_config"]["mlflow"]
        wandb_config = self.config["logging_config"]["wandb"]
        stoppage_config = self.config["stoppage_config"]
        callbacks = self.config.get("callbacks", [])
        tune_config = copy.deepcopy(self.config.get("tune_config"))

        mlflow_callback = CustomMLflowLoggerCallback(
            experiment_name=self.config["name"],
            save_artifact=mlflow_config["save_artifact"],
        )
        callbacks.append(mlflow_callback)

        if wandb_config["api_key_file"] is not None:
            wandb_callback = CustomWandbLoggerCallback(
                project=self.config["name"],
                api_key_file=wandb_config["api_key_file"],
                log_config=wandb_config["log_config"],
                reinit=wandb_config["reinit"],
            )
            callbacks.append(wandb_callback)
        tune_config["callbacks"] = callbacks
        additional_config = tune_config.pop("additional_config")
        tune_config = {**tune_config, **additional_config}
        if "stop" not in stoppage_config:
            tune_config["stop"] = create_stopper(stoppage_config)
        return tune.run(
            TuneTrainer,
            config={
                "trainer_class": self.trainer.__class__,
                "trainer_config": self.config,
            },
            **tune_config
        )
