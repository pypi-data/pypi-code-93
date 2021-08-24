"""This module contains a simulator for converted Smart Nord data.

The models itself are simple data provider.
"""
import logging
import os
from datetime import datetime, timedelta

import mosaik_api
import numpy as np
import pandas as pd
from midas.core.sndata import LOG
from midas.util.base_data_model import DataModel
from midas.util.base_data_simulator import BaseDataSimulator
from midas.util.dateformat import GER

from .meta import INFO, META


class SmartNordDataSimulator(BaseDataSimulator):
    """A simulator for Smart Nord data."""

    def __init__(self):
        super().__init__(META)

        # self.logger = logging.getLogger("midas.sndata")

        self.load_p = None
        self.load_q = None

        self.household_ctr = 0
        self.lvland_ctr = 0
        self.num_households = 0
        self.num_lvlands = 0

    def init(self, sid, **sim_params):
        """Called exactly ones after the simulator has been started.

        :return: the meta dict (set by mosaik_api.Simulator)
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
            data_path, sim_params.get("filename", "SmartNordProfiles.hdf5")
        )
        LOG.debug("Using db file at %s.", file_path)

        self.load_p = pd.read_hdf(file_path, "load_pmw")
        try:
            self.load_q = pd.read_hdf(file_path, "load_qmvar")
        except:
            LOG.debug("No q values for loads available. Skipping.")

        self.num_households = len(self.load_p.columns)
        self.num_lvlands = 8  # TODO store the number of lvlands in db

        return self.meta

    def create(self, num, model, **model_params):
        """Initialize the simulation model instance (entity)

        :return: a list with information on the created entity

        """
        entities = list()
        for _ in range(num):
            eid = f"{model}-{len(self.models)}"

            if model == "Household":
                self.models[eid] = self._create_household(model_params)

            elif model == "Land":
                self.models[eid] = self._create_land(model_params)

            else:
                raise AttributeError(f"Unknown model {model}.")

            entities.append({"eid": eid, "type": model})

        return entities

    def step(self, time, inputs):
        """Perform a simulation step."""
        LOG.debug("At step %d received inputs %s", time, inputs)

        return super().step(time, inputs)

    def get_data(self, outputs):
        """Returns the requested outputs (if feasible)."""
        data = super().get_data(outputs)

        LOG.debug("Gathered outputs %s", data)

        return data

    def _create_household(self, model_params):
        idx = model_params.get("eidx", None)
        if idx is None:
            idx = self.household_ctr
            self.household_ctr = (self.household_ctr + 1) % self.num_households
        else:
            idx = max(0, min(self.num_households, idx))

        col = self.load_p.columns[idx]
        data_q = None
        if self.load_q is not None:
            data_q = self.load_q[col]

        model = DataModel(
            data_p=self.load_p[col],
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

    def _create_land(self, model_params):
        idx = model_params.get("eidx", None)
        if idx is None:
            idx = self.lvland_ctr
            self.lvland_ctr = (self.lvland_ctr + 1) % self.num_lvlands
        else:
            idx = max(0, min(self.num_lvlands, idx))

        hh_per_lvl = INFO[f"Land{idx}"]["num_houses"] - 1
        fkey = f"Load{idx}p000"
        tkey = f"Load{idx}p{hh_per_lvl}"

        data_p = self.load_p.loc[:, fkey:tkey].sum(axis=1)
        data_q = None
        if self.load_q is not None:
            data_q = self.load_q.loc[:, fkey:tkey].sum(axis=1)

        model = DataModel(
            data_p=data_p,
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

    def get_data_info(self):
        return INFO

    def get_data_info(self, eid=None):
        if eid is None:
            INFO
        else:
            return {"p_mwh_per_a": self.models[eid].p_mwh_per_a}


if __name__ == "__main__":
    mosaik_api.start_simulation(SmartNordDataSimulator())
