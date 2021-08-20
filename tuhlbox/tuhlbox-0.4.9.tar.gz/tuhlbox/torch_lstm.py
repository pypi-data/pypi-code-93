"""Basic RNN model."""
from typing import Any

import torch
from torch import nn


class RNNClassifier(nn.Module):
    def __init__(
        self,
        n_classes: int,
        embedding_dim: int = 128,
        rec_layer_type: str = "lstm",
        num_units: int = 128,
        num_layers: int = 2,
        dropout: float = 0.0,
        vocab_size: int = 1000,
    ):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.rec_layer_type = rec_layer_type.lower()
        self.num_units = num_units
        self.num_layers = num_layers
        self.dropout = dropout
        self.n_classes = n_classes

        self.emb = nn.Embedding(vocab_size + 1, embedding_dim=self.embedding_dim)

        rec_layer = {"lstm": nn.LSTM, "gru": nn.GRU}[self.rec_layer_type]
        # We have to make sure that the recurrent layer is batch_first,
        # since sklearn assumes the batch dimension to be the first
        self.rec = rec_layer(
            self.embedding_dim,
            self.num_units,
            num_layers=num_layers,
            batch_first=True,
        )

        self.output = nn.Linear(self.num_units, self.n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        embeddings = self.emb(x)
        # from the recurrent layer, only take the activities from the
        # last sequence step
        if self.rec_layer_type == "gru":
            _, rec_out = self.rec(embeddings)
        else:
            _, (rec_out, _) = self.rec(embeddings)
        rec_out = rec_out[-1]  # take output of last RNN layer
        drop_out = nn.Dropout(p=self.dropout)(rec_out)
        # Remember that the final non-linearity should be softmax, so
        # that our predict_proba method outputs actual probabilities!
        linear_out = self.output(drop_out)
        out = nn.Softmax(dim=-1)(linear_out)
        return out
