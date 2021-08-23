from typing import Any, Optional

from pydantic.dataclasses import dataclass


@dataclass
class WandbLoggerConfig:
    project: Optional[str] = None
    api_key_file: Optional[str] = None
    log_config: bool = False
    reinit: bool = False


@dataclass
class MlflowLoggerConfig:
    experiment_name: Optional[str] = None
    save_artifact: bool = False


@dataclass
class LoggingConfig:
    mlflow: Any = MlflowLoggerConfig()
    wandb: Any = WandbLoggerConfig()
    checkpoint_path: str = "checkpoints"
    tensorboard_log_path: Optional[str] = None
    checkpoint_interval: int = 100
