import logging

from midas.scenario.upgrade_module import UpgradeModule

LOG = logging.getLogger(__name__)


class MarketAgentsModule(UpgradeModule):
    """Market agents upgrade module for MIDAS."""

    def __init__(self, name="marketagents"):
        super().__init__(name, LOG)

        self.default_name = "midasmv"
        self.default_sim_name = "MarketAgents"
        self.default_import_str = "midas.adapter.market_agents:MarketAgentSim"
        self.models = dict()

    def check_module_params(self):
        """Check the module params and provide default values."""
        module_params = self.params.setdefault(f"{self.name}_params", dict())
        if not module_params:
            LOG.debug(
                "No configuration provided. Creating default configuration."
            )
            module_params.setdefault(self.default_name, dict())

        module_params.setdefault("sim_name", self.default_sim_name)
        module_params.setdefault("cmd", "python")
        module_params.setdefault("import_str", self.default_import_str)
        module_params.setdefault("step_size", self.scenario["step_size"])
        module_params.setdefault("start_date", self.scenario["start_date"])

        return module_params

    def check_sim_params(self, module_params, **kwargs):
        """Check the params for a certain simulator instance."""
        self.sim_params.setdefault("sim_name", module_params["sim_name"])
        self.sim_params.setdefault("cmd", module_params["cmd"])
        self.sim_params.setdefault("import_str", module_params["import_str"])
        self.sim_params.setdefault("step_size", module_params["step_size"])
        self.sim_params.setdefault("start_date", module_params["start_date"])
        self.sim_params.setdefault("mapping", dict())

    def start_models(self):
        """Start all models defined in the mapping of a certain simulator."""
        if not self.sim_params["mapping"]:
            self.sim_params["mapping"] = _create_default_mapping()
        mod_ctr = 0
        model = "MarketAgentModel"
        agent_bus_map = dict()

        for unit, bus, uidx in self.sim_params["mapping"]:
            mod_key = self.gen_mod_key(model.lower(), mod_ctr)
            params = {
                "s_max": self.find_sn_mva(unit, bus, uidx),
                "unit_type": unit,
                "start_date": self.sim_params["start_date"],
                "step_size": self.sim_params["step_size"],
            }
            self.start_model(mod_key, model, params)
            agent_bus_map[self.scenario[mod_key].full_id] = bus
            mod_ctr += 1

        self.scenario[
            f"{self.name}_{self.sim_name}_agent_bus_map"
        ] = agent_bus_map

    def gen_mod_key(self, mod_name, eidx):
        return f"{self.name}_{self.sim_name}_{mod_name}_{eidx}"

    def find_sn_mva(self, unit, bus, uidx):
        unit_mod = self.find_unit_mod(unit, bus, uidx)
        em_key = f"der_{self.sim_name}"
        for key, entity in self.scenario.items():
            if em_key in key and "eid_mapping" in key:
                mapping = entity
                break

        return mapping[unit_mod.full_id]["sn_mva"]

    def find_unit_mod(self, unit, bus, uidx):
        ukey = f"der_{self.sim_name}_{unit.lower()}_{bus}"
        candidates = list()
        for key, entity in self.scenario.items():
            if ukey in key:
                candidates.append(entity)

        return candidates[uidx]

    def connect(self):
        mod_ctr = 0
        model = "MarketAgentModel"

        for unit, bus, uidx in self.sim_params["mapping"]:
            mod_key = self.gen_mod_key(model.lower(), mod_ctr)
            agent = self.scenario[mod_key]
            unit_mod = self.find_unit_mod(unit, bus, uidx)
            self.connect_entities(unit_mod, agent, ["schedule"])
            self.connect_entities(
                agent,
                unit_mod,
                [("set_q_schedule", "schedule")],
                time_shifted=True,
                initial_data={"set_q_schedule": None},
            )
            mod_ctr += 1

    def connect_to_db(self):
        LOG.debug("Agents are too proud to connect to a database.")


def _create_default_mapping():
    unit_map = [["PV", 2, 0], ["PV", 3, 0], ["PV", 2, 1], ["PV", 3, 1]]
    return unit_map