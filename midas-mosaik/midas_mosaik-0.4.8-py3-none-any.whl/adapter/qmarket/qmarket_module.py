import logging

from midas.scenario.upgrade_module import UpgradeModule

LOG = logging.getLogger(__name__)


class QMarketModule(UpgradeModule):
    """QMarket upgrade module for MIDAS."""

    def __init__(self, name="qmarket"):
        super().__init__(name, LOG)

        self.default_name = "midasmv"
        self.default_sim_name = "QMarket"
        self.default_import_str = "midas.adapter.qmarket:SimQMarket"
        self.models = {
            "SimQMarket": {
                "attrs": ["agent_bus_map", "u_max", "u_min"],
                "GOA": [("grid", "grid_state")],
                "MarketAgents": {
                    "name": "MarketAgentModel",
                    "from": [("reactive_power_offer", "q_offers")],
                    "to": [("q_accept", "q_set_minutes_15_to_30")],
                    "initial_data": {"q_accept": None},
                },
            }
        }

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
        module_params.setdefault("u_min", 0.96)
        module_params.setdefault("u_max", 1.04)
        return module_params

    def check_sim_params(self, module_params, **kwargs):
        """Check the params for a certain simulator instance."""
        self.sim_params.setdefault("sim_name", module_params["sim_name"])
        self.sim_params.setdefault("cmd", module_params["cmd"])
        self.sim_params.setdefault("import_str", module_params["import_str"])
        self.sim_params.setdefault("step_size", module_params["step_size"])
        self.sim_params.setdefault("start_date", module_params["start_date"])
        self.sim_params.setdefault("u_min", module_params["u_min"])
        self.sim_params.setdefault("u_max", module_params["u_max"])
        self.sim_params.setdefault("agent_bus_map", dict())

    def start_models(self):
        """Start all models defined in the mapping of a certain simulator."""

        if not self.sim_params["agent_bus_map"]:
            self.sim_params["agent_bus_map"] = self.find_agent_bus_map()

        mod_key = self.gen_mod_key()
        params = dict()
        for attr in self.models["SimQMarket"]["attrs"]:
            params[attr] = self.sim_params[attr]

        self.start_model(mod_key, "QMarketModel", params)

    def connect(self):
        self._connect_to_goa()
        self._connect_to_market_agents()

    def connect_to_db(self):
        pass

    def find_agent_bus_map(self):
        abm_key = f"marketagents_{self.sim_name}_agent_bus_map"
        return self.scenario[abm_key]

    def gen_mod_key(self):
        return f"{self.name}_{self.sim_name}_qmarket"

    def _connect_to_goa(self):
        mod_key = self.gen_mod_key()
        for key, entity in self.scenario.items():
            if f"goa_{self.sim_name}" in key:
                goa = entity

        self.connect_entities(
            goa, self.scenario[mod_key], self.models["SimQMarket"]["GOA"]
        )

    def _connect_to_market_agents(self):
        qmarket = self.scenario[self.gen_mod_key()]
        agents = list()
        akey = f"marketagents_{self.sim_name}"
        amod_name = self.models["SimQMarket"]["MarketAgents"]["name"]
        for key, entity in self.scenario.items():
            if akey in key and amod_name.lower() in key:
                agents.append(entity)

        from_attrs = self.models["SimQMarket"]["MarketAgents"]["from"]
        to_attrs = self.models["SimQMarket"]["MarketAgents"]["to"]
        initial_data = self.models["SimQMarket"]["MarketAgents"][
            "initial_data"
        ]
        for agent in agents:

            self.connect_entities(agent, qmarket, from_attrs)
            self.connect_entities(
                qmarket,
                agent,
                to_attrs,
                time_shifted=True,
                initial_data=initial_data,
            )
