import mosaik_api
import numpy as np
from .meta import META


class TimeSimulator(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)

        self.sid = None
        self.eid = None
        self.seconds_day: int = 24 * 60 * 60
        self.seconds_week: int = 24 * 60 * 60 * 7
        self.seconds_year: int = 24 * 60 * 60 * 365
        self.sin_time_day: float = None
        self.cos_time_day: float = None
        self.sin_time_week: float = None
        self.cos_time_week: float = None
        self.sin_time_year: float = None
        self.cos_time_year: float = None

    def init(self, sid, **sim_params):
        self.sid = sid
        self._step_size = sim_params.get("step_size", 900)

        return self.meta

    def create(self, num, model, **model_params):
        errmsg = (
            "You should really not try to instantiate more than one ",
            "timegenerator.",
        )
        assert num == 1 and self.eid is None, errmsg

        self.eid = "Timegenerator-0"
        return [{"eid": self.eid, "type": model}]

    def step(self, time, inputs):
        self.sin_time_day = np.sin(2 * np.pi * time / self.seconds_day)
        self.sin_time_week = np.sin(2 * np.pi * time / self.seconds_week)
        self.sin_time_year = np.sin(2 * np.pi * time / self.seconds_year)
        self.cos_time_day = np.cos(2 * np.pi * time / self.seconds_day)
        self.cos_time_week = np.cos(2 * np.pi * time / self.seconds_week)
        self.cos_time_year = np.cos(2 * np.pi * time / self.seconds_year)

        return time + self._step_size

    def get_data(self, outputs):
        data = dict()
        data[self.eid] = dict()
        data[self.eid]["sin_day_time"] = self.sin_time_day
        data[self.eid]["sin_week_time"] = self.sin_time_week
        data[self.eid]["sin_year_time"] = self.sin_time_year
        data[self.eid]["cos_day_time"] = self.cos_time_day
        data[self.eid]["cos_week_time"] = self.cos_time_week
        data[self.eid]["cos_year_time"] = self.cos_time_year
        return data
