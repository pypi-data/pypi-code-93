from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Type

import torch
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import LabelEncoder
from skorch import NeuralNetClassifier
from torch import nn


class TorchClassifier(ClassifierMixin, BaseEstimator):
    """
    Simple wrapper for Torch modules enabling string labels and dynamic classes.

    Using this wrapper, the model does not need to know the number of classes that the
    problem has. Instead, the number of classes is learned form the fit data.

    Additionally, this wrapper is able to use string labels by using a LabelEncoder.
    """

    def __init__(
        self,
        module: Type[nn.Module],
        max_seq_len: int = None,
        batch_size: int = 64,
        max_epochs: int = 5,
        learn_rate: float = 1e-3,
        device: str = None,
        model_kwargs: Dict[str, Any] = None,
        optimizer: Type[torch.optim.Optimizer] = torch.optim.Adam,
    ):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.module = module
        self.device = device
        self.batch_size = batch_size
        self.max_epochs = max_epochs
        self.learn_rate = learn_rate
        self.model_kwargs = model_kwargs or {}
        self.wrapped_model: Optional[NeuralNetClassifier] = None
        self.optimizer = optimizer
        self.label_encoder: LabelEncoder = LabelEncoder()
        self.max_seq_len = max_seq_len

    def fit(self, x: Any, y: Iterable[Any], **fit_kwargs: Any) -> TorchClassifier:
        if self.wrapped_model is None:
            classes = set(y)
            n_classes = len(classes)
            self.model_kwargs["module__n_classes"] = n_classes
            self.wrapped_model = NeuralNetClassifier(
                module=self.module,
                device=self.device,
                batch_size=self.batch_size,
                max_epochs=self.max_epochs,
                lr=self.learn_rate,
                optimizer=self.optimizer,
                classes=classes,
                **self.model_kwargs
            )
            y = self.label_encoder.fit_transform(y)
        self.wrapped_model.fit(x, y, **fit_kwargs)
        return self

    def predict(self, x: Any) -> Any:
        if self.wrapped_model is None:
            raise ValueError("model was not fitted")
        predicted_classes = self.wrapped_model.predict(x)
        return self.label_encoder.inverse_transform(predicted_classes)
