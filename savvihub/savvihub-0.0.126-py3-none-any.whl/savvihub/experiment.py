import numbers
from typing import Mapping, List

import six

from openapi_client import ResponseExperimentInfo
from savvihub import history
from savvihub.exceptions import ArgumentException
from savvihub.objects import Image


class Experiment:
    def __init__(self, experiment: ResponseExperimentInfo, client):
        self.id = experiment.id
        self.client = client
        self._history = None
        self._plot_volume_id = experiment.experiment_plot_volume

    def get_plot_volume_id(self):
        return self._plot_volume_id

    def refine(self, row, step):
        # Row validation
        if not isinstance(row, Mapping):
            raise ArgumentException(".log() takes a dictionary as a parameter")

        if any(not isinstance(key, six.string_types) for key in row.keys()):
            raise ArgumentException("The key of dictionary in .log() parameter must be str")

        for k in row.keys():
            if not k:
                raise ArgumentException("Logging empty key is not supported")

        # Step validation
        if step is not None:
            if not isinstance(step, numbers.Number):
                raise ArgumentException(f"Step must be a number, not {type(step)}")

            if not isinstance(type(step), int):
                step = int(round(step))

        return row, step

    @classmethod
    def from_given(cls, experiment_id, client):
        return cls(client.experiment_id_read(experiment_id), client)

    @property
    def history(self):
        if not self._history:
            self._history = history.History(self)
        return self._history

    def log(self, row, *, step=None):
        row, step = self.refine(row, step)
        for val in row.values():
            if isinstance(val, List) and len(val) > 0 and all(isinstance(i, Image) for i in val):
                self.history.update_images(self.client, row)
                break
            else:
                self.history.update_metrics(self.client, row, step)
                break
