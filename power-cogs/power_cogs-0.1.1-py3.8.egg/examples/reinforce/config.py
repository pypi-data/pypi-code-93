from dataclasses import field
from typing import Any, List, Optional

from pydantic.dataclasses import dataclass

# internal
from power_cogs.config import Config
from power_cogs.config.trainer_config import TorchTrainerConfig


@dataclass
class RolloutDatasetConfig(Config):
    env_name: str = "LunarLander-v2"
    max_env_steps: int = 10 ** 10
    gamma: float = 0.99
    discount_rewards: bool = True
    normalize_rewards: bool = True
    random_policy: bool = False
    num_rollouts: int = 10
    num_workers: int = 5


@dataclass
class PolicyMLPModelConfig(Config):
    input_dims: Optional[int] = None
    hidden_dims: List[int] = field(default_factory=lambda: [32])
    output_dims: Optional[int] = None
    output_activation: Optional[str] = None
    use_normal_init: bool = True
    normal_std: float = 0.01
    zero_bias: bool = False


@dataclass
class ReinforceTrainerConfig(TorchTrainerConfig):
    dataset_config: Any = RolloutDatasetConfig()
    model_config: Any = PolicyMLPModelConfig()
