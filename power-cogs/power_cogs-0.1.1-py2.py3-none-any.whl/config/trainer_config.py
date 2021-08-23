from dataclasses import field
from typing import Any, List, Optional

from pydantic.dataclasses import dataclass

# internal
from power_cogs.config import Config
from power_cogs.config.cluster_config import LocalClusterConfig
from power_cogs.config.logging_config import LoggingConfig
from power_cogs.config.torch.torch_config import (
    AdamConf,
    DataLoaderConf,
    ExponentialLRConf,
)
from power_cogs.config.tune_config import TuneConfig


@dataclass
class EarlyStoppageConfig(Config):
    batch_size: int = 32
    epochs: int = 1000
    early_stoppage: bool = False
    loss_threshold: float = -float("inf")
    stop: Optional[Any] = None
    callbacks: List[Any] = field(default_factory=lambda: [])


@dataclass
class TrainerConfig(Config):
    name: Optional[str] = None
    visualize: bool = False
    batch_size: int = 32
    epochs: int = 1000
    early_stoppage: bool = False
    logging_config: Any = LoggingConfig()
    stoppage_config: Any = EarlyStoppageConfig()
    tune_config: Any = TuneConfig()

    def overrides(self):
        self.stoppage_config.batch_size = self.batch_size
        self.stoppage_config.epochs = self.epochs
        self.stoppage_config.early_stoppage = self.early_stoppage
        self.tune_config.checkpoint_freq = self.logging_config.checkpoint_interval


@dataclass
class TorchTrainerConfig(TrainerConfig):
    optimizer_config: Any = AdamConf()
    scheduler_config: Any = ExponentialLRConf()
    dataloader_config: Any = DataLoaderConf()
    cluster_config: Any = LocalClusterConfig()
