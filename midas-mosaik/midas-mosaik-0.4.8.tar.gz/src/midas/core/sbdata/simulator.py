"""This module contains a simulator for data extracted from simbench.

The models itself are simple data provider.
"""
import os
from datetime import datetime, timedelta

import mosaik_api
import numpy as np
import pandas as pd
from midas.core.sbdata import LOG
from midas.util.base_data_model import DataModel
from midas.util.base_data_simulator import BaseDataSimulator
from midas.util.dateformat import GER

from .meta import META


class SimbenchDataSimulator(BaseDataSimulator):
    """A simulator for simbench data."""

    def __init__(self):
        super().__init__(META)

        self.load_p = None
        self.load_q = None
        self.sgen_p = None
        self.sgen_q = None

        self.num_models = dict()
        self.load_ctr = 0
        self.sgen_ctr = 0
        self.num_loads = 0
        self.num_sgens = 0

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
            The meta dict (set by mosaik_api.Simulator)

        """
        super().init(sid, **sim_params)

        # Load the data
        data_path = sim_params.get(
            "data_path",
            os.path.abspath(
                os.path.join(__file__, "..", "..", "..", "..", "..", "data")
            ),
        )
        file_path = os.path.join(
            data_path, sim_params.get("filename", "1-LV-rural3--0-sw.hdf5")
        )
        LOG.debug("Using db file at %s.", file_path)

        self.load_p = pd.read_hdf(file_path, "load_pmw")
        self.load_q = pd.read_hdf(file_path, "load_qmvar")
        self.sgen_p = pd.read_hdf(file_path, "sgen_pmw")
        try:
            self.sgen_q = pd.read_hdf(file_path, "sgen_qmvar")
        except KeyError:
            LOG.debug("No q values for sgens available. Skipping.")

        self.num_loads = len(self.load_p.columns)
        self.num_sgens = len(self.sgen_p.columns)

        return self.meta

    def create(self, num, model, **model_params):
        """Initialize the simulation model instance (entity)

        :return: a list with information on the created entity

        """
        entities = list()
        self.num_models.setdefault(model, 0)
        for _ in range(num):
            eid = f"{model}-{self.num_models[model]}"

            if model == "Load":
                self.models[eid] = self._create_load(model_params)

            elif model == "Sgen":
                self.models[eid] = self._create_sgen(model_params)

            else:
                raise AttributeError(f"Unknown model {model}.")

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
        """Return the requested outputs (if feasible).

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

    def _create_load(self, model_params):
        idx = model_params.get("eidx", None)
        if idx is None:
            idx = self.load_ctr
            self.load_ctr = (self.load_ctr + 1) % self.num_loads
        else:
            idx = max(0, min(self.num_loads, idx))

        model = DataModel(
            data_p=self.load_p[idx],
            data_q=self.load_q[idx],
            data_step_size=900,
            scaling=model_params.get("scaling", 1.0),
            seed=self.rng.randint(self.seed_max),
            interpolate=model_params.get("interpolate", self.interpolate),
            randomize_data=model_params.get(
                "randomize_data", self.randomize_data
            ),
            randomize_cos_phi=model_params.get(
                "randomize_cos_phi", self.randomize_cos_phi
            ),
        )
        return model

    def _create_sgen(self, model_params):
        idx = model_params.get("eidx", None)
        if idx is None:
            idx = self.sgen_ctr
            self.sgen_ctr = (self.sgen_ctr + 1) % self.num_sgens
        else:
            idx = max(0, min(self.num_sgens, idx))

        data_q = None
        if self.sgen_q is not None:
            data_q = self.sgen_q[idx]

        model = DataModel(
            data_p=self.sgen_p[idx],
            data_q=data_q,
            data_step_size=900,
            scaling=model_params.get("scaling", 1.0),
            seed=self.rng.randint(self.seed_max),
            interpolate=model_params.get("interpolate", self.interpolate),
            randomize_data=model_params.get(
                "randomize_data", self.randomize_data
            ),
            randomize_cos_phi=model_params.get(
                "randomize_cos_phi", self.randomize_cos_phi
            ),
        )
        return model

    def get_data_info(self, eid=None):
        if eid is None:
            return {"num_loads": self.num_loads, "num_sgens": self.num_sgens}

        else:
            return {"p_mwh_per_a": self.models[eid].p_mwh_per_a}


if __name__ == "__main__":
    mosaik_api.start_simulation(SimbenchDataSimulator())
