"""Basic CNN model."""
import math
from typing import List, Tuple

import torch
import torch.nn as nn


def compute_first_fc_layer_input_size(
    conv_configs: List[Tuple[int, int]], n: int
) -> int:
    """
    Calculates the input dimension of the first fully connected layer.

    See https://datascience.stackexchange.com/a/40991/9281

    Args:
        conv_configs: Configurations of the convolution or max-pool layer, each a tuple
            with (kernel_size, stride) values.
        n: starting value (max sequence length)

    Returns:
        the dimension of the first fc layer
    """

    def get_output_dim(in_size: int, kernel: int, stride: int) -> int:
        return math.floor(((in_size - kernel) / stride) + 1)

    for config in conv_configs:
        n = get_output_dim(n, config[0], config[1])

    return n


class CharCNN(nn.Module):
    """Basic CNN model that can be built with variable amounts of layers etc."""

    def __init__(
        self,
        n_classes: int,
        max_seq_len: int,
        embedding_dim: int = 300,
        num_features: int = 10_000,
    ):
        super().__init__()
        self.emb_layer = nn.Embedding(num_features + 1, embedding_dim)
        self.conv_layers = nn.Sequential(
            nn.Conv1d(embedding_dim, 50, (7,), (1,)),
            nn.ReLU(),
            nn.MaxPool1d(3, 3),
            nn.Conv1d(50, 50, (5,), (1,)),
            nn.ReLU(),
            nn.MaxPool1d(3, 3),
        )
        self.fc_layers = nn.Sequential(
            nn.Linear(450, 200),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(200, n_classes),
            nn.Softmax(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:

        x = self.emb_layer(x)

        # the embedding layer returns the values in format:
        #
        #    (batch_size, sequence_length, embedding_dimension)
        #
        # but the convolution layers expect
        #
        #    (batch_size, num_filters, sequence_length)
        #
        # in order to convolute correctly on the last dimension.
        # this operation swaps the last two elements:
        x = x.permute(0, 2, 1)

        for conv in self.conv_layers:
            x = conv(x)
        # flatten all values
        x = x.view(x.size(0), -1)
        for fc in self.fc_layers:
            x = fc(x)
        return x
