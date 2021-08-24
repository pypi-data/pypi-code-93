"""This module contains the default load profile data model."""
import numpy as np

from midas.util.compute_q import compute_q


class DLPModel:
    """A model to handle a default load profile."""

    def __init__(self, data, p_mwh_per_a, **params):
        self.data = data
        self.p_kwh_per_a = p_mwh_per_a * 3.500  # ?

        self.rng = np.random.RandomState(params.get("seed", None))

        self.interpolate = params.get("interpolate", False)
        self.randomize_data = params.get("randomize_data", False)
        self.randomize_cos_phi = params.get("randomize_cos_phi", False)

        # Inputs
        self.now_dt = None
        self.cos_phi = None

        # Outputs
        self.p_mw = None
        self.q_mvar = None

    def step(self):
        """Generate the data for the next time interval defined by
        now_dt.

        """
        if self.now_dt.month in {1, 2, 12}:
            season = "winter"
        elif self.now_dt.month in {6, 7, 8}:
            season = "summer"
        else:
            season = "transition"

        if self.now_dt.weekday() == 5:
            day = "saturday"
        elif self.now_dt.weekday() == 6:
            day = "sunday"
        else:
            day = "weekday"

        idx = int(self.now_dt.hour * 4 + self.now_dt.minute // 15)
        if self.interpolate:
            cur_sec = self.now_dt.minute * 60 + self.now_dt.second
            f_p = self.data[season][day][idx : idx + 2]
            if len(f_p) == 1:
                f_p = np.array([f_p[0], self.data[season][day][0]])
            self.p_mw = np.interp(cur_sec, [0, 3_600], f_p)
        else:
            self.p_mw = self.data[season][day][idx]

        if self.randomize_data:
            self.p_mw *= self.rng.normal(scale=0.05, loc=1.0)
            self.p_mw = max(0, self.p_mw)

        if self.randomize_cos_phi:
            self.cos_phi = max(
                0, min(2 * np.pi, self.rng.normal(scale=0.01, loc=0.9))
            )

        self.p_mw *= self.p_kwh_per_a * 1e-6
        self.q_mvar = compute_q(self.p_mw, self.cos_phi)
