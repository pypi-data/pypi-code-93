""" This module contains the DLP simulator."""
import os

import h5py
import mosaik_api
import numpy as np
from midas.core.dlp import LOG
from midas.core.dlp.model import DLPModel
from midas.util.base_data_simulator import BaseDataSimulator

from .meta import META


class DLPSimulator(BaseDataSimulator):
    """The DLP simulator."""

    def __init__(self):
        super().__init__(META)
        self.sid = None
        self.models = dict()
        self.num_models = dict()
        self.data = dict()

    def init(self, sid, **sim_params):
        """Called exactly ones after the simulator has been started.

        Parameters
        ----------
        sid : str
            Simulator ID for this simulator.
        step_size : int, optional
            Step size for this simulator. Defaults to 900.

        Returns
        -------
        dict
            The meta dict (set by *mosaik_api.Simulator*).
        """
        super().init(sid, **sim_params)

        data_path = sim_params.get(
            "data_path",
            os.path.abspath(
                os.path.join(__file__, "..", "..", "..", "..", "..", "data")
            ),
        )
        file_path = os.path.join(
            data_path, sim_params.get("file_name", "DefaultLoadProfiles.hdf5")
        )
        LOG.debug("Using db file at %s.", file_path)

        with h5py.File(file_path, "r") as h5f:
            for profile in h5f:
                self.data.setdefault(profile, dict())
                for season in h5f[profile]:
                    self.data[profile].setdefault(season, dict())
                    for day in h5f[profile][season]:
                        self.data[profile][season][day] = np.array(
                            list(h5f[profile][season][day])
                        )
        return self.meta

    def create(self, num, model, **model_params):
        """Initialize the simulation model instance (entity).

        Parameters
        ----------
        num : int
            The number of models to create.
        model : str
            The name of the models to create. Must be present inside
            the simulator's meta.

        Returns
        -------
        list
            A list with information on the created entity.
        """

        entities = list()
        self.num_models.setdefault(model, 0)
        for _ in range(num):
            eid = f"{model}-{self.num_models[model]}"
            profile = model[-2:]
            self.models[eid] = DLPModel(
                data=self.data[profile],
                p_mwh_per_a=model_params["p_mwh_per_a"],
                seed=self.rng.randint(self.seed_max),
                interpolate=model_params.get("interpolate", self.interpolate),
                randomize_data=model_params.get(
                    "randomize_data", self.randomize_data
                ),
                randomize_cos_phi=model_params.get(
                    "randomize_cos_phi", self.randomize_cos_phi
                ),
            )

            self.num_models[model] += 1
            entities.append({"eid": eid, "type": model})

        return entities

    def step(self, time, inputs):
        """Perform a simulation step.

        Parameters
        ----------
        time : int
            The current simulation step (by convention in seconds since
            simulation start.
        inputs : dict
            A *dict* containing inputs for entities of this simulator.

        Returns
        -------
        int
            The next step this simulator wants to be stepped.

        """
        LOG.debug("At step %d received inputs %s", time, inputs)

        return super().step(time, inputs)

    def get_data(self, outputs):
        """Return the requested output (if feasible).

        Parameters
        ----------
        outputs : dict
            A *dict* containing requested outputs of each entity.

        Returns
        -------
        dict
            A *dict* containing the values of the requested outputs.

        """

        data = super().get_data(outputs)

        LOG.debug("Gathered outputs %s", data)

        return data


if __name__ == "__main__":
    mosaik_api.start_simulation(DLPSimulator())
