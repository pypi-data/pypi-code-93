import torch

from power_cogs.base.torch.base_torch_model import BaseTorchModel
from power_cogs.config.config import class_config
from power_cogs.examples.mnist.config import MNISTModelConfig
from power_cogs.utils.torch_utils import create_linear_network


@class_config(MNISTModelConfig)
class MNISTModel(BaseTorchModel):
    def __init__(self, config={}):
        super(MNISTModel, self).__init__(config)
        self.input_dims = config.get("input_dims")
        self.hidden_dims = config.get("hidden_dims")
        self.output_dims = config.get("output_dims")
        self.output_activation = config.get("output_activation")
        self.use_normal_init = config.get("use_normal_init")
        self.normal_std = config.get("normal_std")
        self.zero_bias = config.get("zero_bias")
        if self.output_activation is not None:
            self.output_activation = eval(self.output_activation)
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
            x = self.output_activation(x)
        return x
