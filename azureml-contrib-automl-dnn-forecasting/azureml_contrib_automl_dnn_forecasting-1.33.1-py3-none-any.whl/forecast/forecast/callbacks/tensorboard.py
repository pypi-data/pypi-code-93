"""Logs all losses and metrics to Tensorboard."""

from typing import Callable, Mapping, Optional, Sequence, Union

from torch.utils.tensorboard import SummaryWriter

from forecast.callbacks import Callback
from forecast.models import ForecastingModel


# A TBCallback is passed the SummarWriter, the model, the current epoch, the current loss, and a dict of metrics
TBCallback = Callable[[SummaryWriter, ForecastingModel, int, float, Mapping[str, float]], None]


def _normalize_to_list(cb: Optional[Union[TBCallback, Sequence[TBCallback]]]) -> Sequence[TBCallback]:
    if not cb:
        return []
    elif callable(cb):
        return [cb]
    elif isinstance(cb, Sequence):
        return cb
    else:
        raise TypeError('Input must be of type None, TBCallback, or Sequence[TBCallback]')


class TensorboardCallback(Callback):
    """Logs all losses and metrics to Tensorboard."""

    def __init__(self,
                 out_dir: str,
                 tb_train_callbacks: Optional[Union[TBCallback, Sequence[TBCallback]]] = None,
                 tb_val_callbacks: Optional[Union[TBCallback, Sequence[TBCallback]]] = None):
        """Logs all losses and metrics to Tensorboard.

        Parameters
        ----------
        out_dir: str
            The directory to which the TFEvents file will be written
        tb_train_callbacks: Union[TBCallback, Sequence[TBCallback]], optional
            One or more callbacks which are invoked at the end of each training epoch. Allows for the logging to
            tensorboard of non-metric values, e.g., an embedding.
        tb_train_callbacks: Union[TBCallback, Sequence[TBCallback]], optional
            One or more callbacks which are invoked at the end of each validation epoch.

        """
        super().__init__()
        self._writer = SummaryWriter(out_dir)
        self._train_cb = _normalize_to_list(tb_train_callbacks)
        self._val_cb = _normalize_to_list(tb_val_callbacks)

    def on_train_epoch_end(self, epoch: int, loss: float, metrics: Mapping[str, float]) -> None:
        """Writes the training loss and metrics to the TFEvents file at the end of an epoch.

        Parameters
        ----------
        epoch: int
            The current epoch
        loss: float
            The training loss for the current epoch
        metrics: Mapping[str, float]
            The training metrics computed for the current epoch

        Returns
        -------
        None

        """
        assert self._model is not None

        self._writer.add_scalar('train/loss', loss, epoch)
        for name, metric in metrics.items():
            self._writer.add_scalar(f'train/{name}', metric, epoch)
        for cb in self._train_cb:
            cb(self._writer, self._model, epoch, loss, metrics)

    def on_val_end(self, epoch: int, loss: float, metrics: Mapping[str, float]) -> None:
        """Writes the validation loss and metrics to the TFEvents file at the end of an epoch.

        Parameters
        ----------
        epoch: int
            The current epoch
        loss: float
            The validation loss for the current epoch
        metrics: Mapping[str, float]
            The validation metrics computed for the current epoch

        Returns
        -------
        None

        """
        assert self._model is not None

        self._writer.add_scalar('val/loss', loss, epoch)
        for name, metric in metrics.items():
            self._writer.add_scalar(f'val/{name}', metric, epoch)
        for cb in self._val_cb:
            cb(self._writer, self._model, epoch, loss, metrics)

    def on_train_end(self) -> None:
        """Flushes and closes Tensorboard events file."""
        self._writer.close()
