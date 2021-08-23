import typing

import numpy as np
import torch
from sklearn import datasets

# internal
from power_cogs.base.torch.base_torch_dataset import BaseTorchDataset


class MNISTDataset(BaseTorchDataset):
    def __init__(self):
        super(MNISTDataset, self).__init__()
        data = datasets.load_digits()
        self.data = torch.from_numpy(data["data"] / 255.0)
        self.targets = torch.from_numpy(data["target"])
        self.input_dims = self.data.shape[-1]
        self.output_dims = np.unique(self.targets).shape[0]

    def __len__(self) -> int:
        return self.data.shape[0]

    def __getitem__(self, index: int) -> typing.Dict[str, typing.Any]:
        return {
            "data": self.data[index],
            "targets": self.targets[index],
            "indices": index,
        }

    def to_device(self, device: torch.device):
        self.data.to(device)
        self.targets.to(device)
