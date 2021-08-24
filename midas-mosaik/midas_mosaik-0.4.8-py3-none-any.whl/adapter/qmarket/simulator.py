# qmarket.py
"""
Mosaik API to minimalistic reactive power market model.

Author: Thomas Wolgast <thomas.wolgast@uol.de>

"""

import mosaik_api

# import qmarket

from midas.adapter.qmarket import LOG
from midas.adapter.qmarket.model import QMarketModel
from midas.adapter.qmarket.meta import META


class SimQMarket(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = "QMarketModel_"
        self.model_name = "Model_qmarket"
        self.entities = {}  # Maps EIDs to model indices in self.simulator

    def init(self, sid, **sim_params):
        self.step_size = sim_params.get("step_size", 900)
        if sim_params.get("eid_prefix", None) is not None:
            self.eid_prefix = sim_params["eid_prefix"]
        return self.meta

    def create(self, num, model, **model_params):
        # Only one market entity possible
        assert num == 1
        assert self.entities == {}

        idx = 0
        eid = f"{self.eid_prefix}{idx}"
        self.entities[eid] = idx
        entities = [{"eid": eid, "type": model}]
        self.simulator = QMarketModel(model_params)

        return entities

    def step(self, time, inputs):
        LOG.debug("At step %d received inputs %s", time, inputs)
        # print("qmarket step ", time, "\n")
        for model_inputs in inputs.values():
            for attr, values in model_inputs.items():
                if attr == "q_offers":
                    q_offers = values
                elif attr == "grid_state":
                    # TODO: keys useless here#
                    assert len(values.values()) == 1
                    grid_state = list(values.values())[0]
        self.q_accept = self.simulator.step(grid_state, q_offers)

        return time + self.step_size

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            data[eid] = {}
            for attr in attrs:
                if attr not in self.meta["models"]["QMarketModel"]["attrs"]:
                    raise ValueError(f"Unknown output attribute: {attr}")

                data[eid][attr] = getattr(self.simulator, attr)

        LOG.debug("Gathered outputs %s.", data)
        return data


def main():
    return mosaik_api.start_simulation(SimQMarket())


if __name__ == "__main__":
    main()
