from dataclasses import field
from typing import Any, List, Optional

from pydantic.dataclasses import dataclass

# internal
from power_cogs.config import Config
from power_cogs.config.trainer_config import TorchTrainerConfig


@dataclass
class MNISTModelConfig(Config):
    input_dims: int = 64
    hidden_dims: List[int] = field(default_factory=lambda: [32, 32])
    output_dims: int = 10
    output_activation: Optional[str] = None
    use_normal_init: bool = True
    normal_std: float = 1.0
    zero_bias: bool = False


@dataclass
class MNISTTrainerConfig(TorchTrainerConfig):
    model_config: Any = MNISTModelConfig()
