"""This module contains the MIDAS upgrade for rettij."""
import logging
import os
import sys

from midas.scenario.upgrade_module import UpgradeModule

LOG = logging.getLogger(__name__)


class RettijModule(UpgradeModule):
    """Rettij upgrade module for MIDAS."""

    def __init__(self):
        super().__init__("rettij", LOG)

        self.default_name = "midasmv"
        self.default_sim_name = "SimRettij"
        self.default_import_str = "simulators.rettij.rettij:SimRettij"
        self.models = {}

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
        module_params.setdefault(
            "rettij_cfg_path", os.path.abspath(os.path.join("co-simulation"))
        )
        module_params.setdefault(
            "rettij_path", os.path.abspath(os.path.join("rettij"))
        )
        sys.path.insert(0, module_params["rettij_path"])
        sys.path.insert(0, module_params["rettij_cfg_path"])

        return module_params

    def check_sim_params(self, module_params, **kwargs):
        """Check the params for a certain simulator instance."""
        self.sim_params.setdefault("sim_name", module_params["sim_name"])
        self.sim_params.setdefault("cmd", module_params["cmd"])
        self.sim_params.setdefault("import_str", module_params["import_str"])
        self.sim_params.setdefault("step_size", module_params["step_size"])
        self.sim_params.setdefault("cluster_config", "k3s.yaml")
        self.sim_params.setdefault(
            "network", "simple_pyrate-topology_minimal.yml"
        )
        self.sim_params.setdefault("scenario", "rettij_sequence.py")
        self.sim_params.setdefault("custom-components")
        self.sim_params.setdefault("rettij_nodes", dict())
        # self.sim_params.setdefault("start_date", module_params[""])

    def start_models(self):
        """Start all models defined in the mapping of a certain simulator."""

        mod_key = self.gen_mod_key()
        params = dict()

        self.start_model(mod_key, "SimRettij", params)

        if not self.sim_params["rettij_nodes"]:
            mod = self.scenario[mod_key]
            self.sim_params["rettij_nodes"] = {
                ent.eid: ent for ent in mod.children
            }

        print("Rettij added")

    def connect(self):

        for node_id, node in self.sim_params["rettij_nodes"].items():
            print(node_id, node)

    def connect_to_db(self):
        pass

    def gen_mod_key(self):
        return f"{self.name}_{self.sim_name}_rettij"