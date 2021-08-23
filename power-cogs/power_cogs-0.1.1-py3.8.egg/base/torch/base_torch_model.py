from typing import Any

import torch
from torchsummaryX import summary

from power_cogs.base.base import Base


class BaseTorchModel(Base, torch.nn.Module):
    def __init__(self, config: Any):
        super(BaseTorchModel, self).__init__()
        self.config = config

    def summary(self, input_shape):
        summary(self, input_shape)
