import mosaik_api
import pandas as pd
import warnings
from tables import NaturalNameWarning

warnings.filterwarnings("ignore", category=NaturalNameWarning)

META = {
    "models": {
        "Database": {
            "public": True,
            "any_inputs": True,
            "params": ["filename", "verbose"],
            "attrs": [],
        }
    }
}


class MidasHdf5(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)

        self.sid = None
        self.eid = "Database"
        self.database = None
        self.filename = None
        self.step_size = None
        self.finalized = False

    def init(self, sid, **sim_params):
        self.sid = sid
        self.step_size = sim_params.get("step_size", 900)

        return self.meta

    def create(self, num, model, **model_params):
        errmsg = (
            "You should realy not try to instantiate more than one "
            "database. If your need another database, create a new "
            "simulator as well."
        )
        assert self.database is None, errmsg
        assert num == 1, errmsg

        self.filename = model_params.get("filename", None)
        if self.filename is not None and not self.filename.endswith(".hdf5"):
            self.filename = f"{self.filename}.hdf5"
        self.database = dict()

        return [{"eid": self.eid, "type": model}]

    def step(self, time, inputs):
        data = inputs[self.eid]
        abs_idx = time // self.step_size

        current = dict()
        for attr, src_ids in data.items():
            for src_id, val in src_ids.items():
                sid, eid = src_id.split(".")
                key = f"{eid}.{attr}"

                current.setdefault(sid, dict())
                current[sid].setdefault("cols", list()).append(key)
                current[sid].setdefault("vals", list()).append(val)

        for sid, data in current.items():
            self.database.setdefault(sid, pd.DataFrame())

            ndf = pd.DataFrame([data["vals"]], columns=data["cols"])

            self.database[sid] = self.database[sid].append(
                ndf, ignore_index=True
            )
        return time + self.step_size

    def get_data(self, outputs):
        return dict()

    def finalize(self):
        if self.finalized:
            return
        else:
            self.finalized = True

        for sid, data in self.database.items():
            data.to_hdf(self.filename, sid)
