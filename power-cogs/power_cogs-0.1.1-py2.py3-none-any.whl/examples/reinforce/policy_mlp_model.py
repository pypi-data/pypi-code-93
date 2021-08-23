from typing import Any

import torch

from power_cogs.base.torch.base_torch_model import BaseTorchModel
from power_cogs.config.config import class_config
from power_cogs.examples.reinforce.config import PolicyMLPModelConfig
from power_cogs.utils.torch_utils import create_linear_network


@class_config(PolicyMLPModelConfig)
class PolicyMLPModel(BaseTorchModel):
    def __init__(self, config: Any = {}):
        super(PolicyMLPModel, self).__init__(config)
        self.input_dims = config.get("input_dims")
        self.hidden_dims = config.get("hidden_dims")
        self.output_dims = config.get("output_dims")
        self.use_normal_init = config.get("use_normal_init")
        self.normal_std = config.get("normal_std")
        self.zero_bias = config.get("zero_bias")
        output_activation = config.get("output_activation")
        if output_activation is not None:
            self.output_activation = eval(output_activation)
        else:
            self.output_activation = None
        self.net = create_linear_network(
            self.input_dims, self.hidden_dims, self.output_dims
        )

        def init_weights(m):
            if isinstance(m, torch.nn.Linear):
                torch.nn.init.normal_(m.weight, std=self.normal_std)
                if getattr(m, "bias", None) is not None:
                    if self.zero_bias:
                        torch.nn.init.zeros_(m.bias)
                    else:
                        torch.nn.init.normal_(m.bias, std=self.normal_std)

        if self.use_normal_init:
            with torch.no_grad():
                self.apply(init_weights)

    def forward(self, x):
        x = self.net(x)
        if self.output_activation is not None:
            return self.output_activation(x)
        else:
            return x

    def forward_policy(self, x):
        return self.forward(x)
