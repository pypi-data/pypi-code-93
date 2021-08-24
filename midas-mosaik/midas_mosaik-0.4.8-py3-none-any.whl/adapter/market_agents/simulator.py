"""Mosaik interface for the MarketAgentSim.

Author: Torge Wolff <torge.wolff@offis.de>
"""
import mosaik_api
from midas.adapter.market_agents.model import MarketAgentModel

from midas.adapter.market_agents import LOG
from midas.adapter.market_agents.meta import META


class MarketAgentSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.sid = None
        self.step_size = 60 * 15
        self.models = []
        self.num_models = 0
        self.eid_prefix = "MarketAgentModel_"
        self.entities = {}  # Maps EIDs to model indices in self.simulator
        self.last_time = -self.step_size
        self.place_offer_state = True

    def init(self, sid, **sim_params):
        """
        Called exactly ones after the simulator has been started.
        :return: the meta dict (set by mosaik_api.Simulator)
        """
        self.sid = sid
        if sim_params.get("eid_prefix", None) is not None:
            self.eid_prefix = sim_params["eid_prefix"]

        return self.meta

    def create(self, num, model, unit_type, s_max, start_date, step_size):
        """
        Initialize the simulation model instance (entity)
        :return: a list with information on the created entity
        """
        next_eid = len(self.entities)
        entities = []

        for i in range(next_eid, next_eid + num):
            prefix = self.eid_prefix + unit_type + "_"
            eid = "%s%d" % (prefix, i)
            new_model = MarketAgentModel(
                sid=self.sid,
                eid=eid,
                unit_type=unit_type,
                s_max=s_max,
                start_date=start_date,
                step_size=step_size,
            )
            self.models.append({eid: new_model})
            self.num_models += 1
            self.entities[eid] = i
            entities.append({"eid": eid, "type": model})

        return entities

    def step(self, time, inputs):
        """Perform a simulation step"""
        # Get inputs
        LOG.debug("At step %d received inputs %s", time, inputs)
        q_set_minutes_15_to_30 = None
        schedule = None
        for eid, attrs in inputs.items():
            model_idx = self.entities[eid]
            for attr, values in attrs.items():
                if attr == "schedule":
                    schedule = [v for k, v in values.items()]
                    schedule = schedule[-1]

                elif attr == "q_set_minutes_15_to_30":
                    # extract q_set values from market operator
                    for from_eid, value in values.items():
                        if not value:
                            q_set_minutes_15_to_30 = None
                        else:
                            q_set_minutes_15_to_30 = value.get(
                                self.sid + "." + eid, None
                            )
                            if q_set_minutes_15_to_30 is None:
                                LOG.debug(
                                    "q_set is None for %s.%s", self.sid, eid
                                )

            if self.place_offer_state:
                self.models[model_idx][eid].create_q_offer(
                    time=time,
                    schedule=schedule,
                    sim_place_offer_state=self.place_offer_state,
                )
            else:
                self.models[model_idx][eid].set_q_values(
                    time=time,
                    q_set_minutes_15_to_30=q_set_minutes_15_to_30,
                    sim_place_offer_state=self.place_offer_state,
                )

        if self.place_offer_state:
            # wakeup_time = time + 1
            self.place_offer_state = False
        else:
            # wakeup_time = time + self.step_size - 1
            self.place_offer_state = True
        wakeup_time = time + self.step_size // 2
        LOG.debug("Set wakeup time in step: %d.", wakeup_time)
        return wakeup_time

    def get_data(self, outputs):
        """Returns the requested outputs (if feasible)"""
        data = {}
        for eid, attrs in outputs.items():
            model_idx = self.entities[eid]
            data[eid] = {}
            for attr in attrs:
                if (
                    attr
                    not in self.meta["models"]["MarketAgentModel"]["attrs"]
                ):
                    raise ValueError("Unknown output attribute: %s" % attr)

                data[eid][attr] = getattr(
                    self.models[model_idx].get(eid), attr
                )
        LOG.debug("Gathered outputs %s.", data)
        return data


def main():
    return mosaik_api.start_simulation(MarketAgentSim())


if __name__ == "__main__":
    main()