"""This module contains the configurator for midas scenarios."""
import os
from importlib import import_module

from ruamel.yaml import YAML

from midas.scenario import LOG
from midas.util.dict_util import update, convert
from midas.util.logging_util import setup_logging
from midas.tools import config

MODULES = [
    ("powergrid", "PowergridModule"),
    ("sbdata", "SimbenchDataModule"),
    ("sndata", "SmartNordDataModule"),
    ("comdata", "CommercialDataModule"),
    ("weather", "WeatherDataModule"),
    ("der", "PysimmodsModule"),
    ("goa", "GridOperatorModule"),
    ("messages", "MessagesModule"),
]


class Configurator:
    """This is the main configurator for midas scenarios.

    The configurator takes at least a scenario name to create a fully-
    configured mosaik scenario.

    Parameters
    ----------
    scenario_name : str
        A *str* containing the name of the scenario_name which should
        be run.
    params : dict
        A *dict* with the pre-configuration for the scenario.
        Can be empty.
    config : str
        A *string* containing the path to a custom config file.

    Attributes
    ----------
    custom_cfg : str
        Stores the path to the custom configuration if provided
    params : dict
        A *dict* containing the configuration of the scenario. The dict
        is extended during the configuration.
    scenario : dict
        A *dict* containing references to everything that is created
        during the configuration of the senario.
    scenario_name : str
        The name of the scenario created

    """

    def __init__(self, inipath=None, datapath=None, autocfg=False):
        self.midascfg = config.check_config(inipath)
        if self.midascfg is None:
            config.dialog(inipath, datapath, autocfg)
            self.midascfg = config.check_config(inipath)
        config.check_data(self.midascfg)

        self.scenario_name: str
        self.params: dict
        self.custom_cfgs: list
        self.scenario: dict

    def configure(self, scenario_name, params, custom_cfg=None):
        """Configure the midas scenario.

        Will use the information provided during initialization.

        Returns
        -------
        dict
            A *dict* containing everything that was defined during
            configuration.

        """
        LOG.info("Starting configuration of the scenario %s...", scenario_name)
        self.scenario_name = scenario_name
        self.params = params

        dirpath = os.path.split(__file__)[0]
        dirpath = os.path.join(dirpath, "config")
        os.makedirs(os.path.abspath(dirpath), exist_ok=True)

        files = os.listdir(dirpath)

        if custom_cfg is not None and not isinstance(custom_cfg, list):
            custom_cfg = [custom_cfg]
        self.custom_cfgs = custom_cfg

        if self.custom_cfgs is not None:
            for ccfg in self.custom_cfgs:
                if not ccfg.endswith(".yml"):
                    ccfg = f"{ccfg}.yml"
                if not ccfg.startswith("/"):
                    ccfg = os.path.abspath(ccfg)

                if os.path.isfile(ccfg):
                    LOG.debug("Adding custom config at %s.", ccfg)
                    files.append(ccfg)
                else:
                    LOG.warn("Did not found config %s.", ccfg)

        if len(files) == 0:
            LOG.error("No configuration files found. Aborting!")
            return dict()

        configs = self._load_configs(dirpath, files)
        params = self._organize_params(configs)

        self.scenario = {
            "scenario_name": self.scenario_name,
        }
        self._apply_modules(self.scenario, params)

        self._save_config(self.scenario_name, params)
        self._save_script(self.scenario["script"])
        LOG.info("Configuration finished.")
        return self.scenario

    def run(self):
        """Run the scenario configured before."""

        if self.scenario is None:
            LOG.error(
                "Scenario is not configured. "
                "Maybe you forgot to call configure?"
            )
            return

        LOG.info("Starting the scenario ...")
        self.scenario["world"].run(
            until=self.scenario["end"],
            print_progress=not self.params["silent"],
        )
        LOG.info("Scenario finished.")

    def _organize_params(self, configs):
        """Sort params in correct order."""
        try:
            cfg_chain = [configs[self.scenario_name]]
        except KeyError as k_e:
            LOG.critical(
                "%s not found in config files. Cannot process any further.",
                self.scenario_name,
            )
            raise k_e

        parent = cfg_chain[0]["parent"]
        while parent is not None and parent != "None":
            cfg_chain.append(configs[parent])
            parent = cfg_chain[-1]["parent"]

        LOG.debug("Ordering the configs ...")
        modules = list()
        final_params = dict()
        for cfg in reversed(cfg_chain):
            modules += cfg["modules"]
            update(final_params, cfg)
        final_params["modules"] = modules

        update(final_params, self.params)
        LOG.debug("Normalizing the config ...")
        self._normalize(final_params)

        return final_params

    def _load_configs(self, dirpath, files):
        """Load the config files with yaml."""

        configs = dict()
        yaml = YAML(typ="safe", pure=True)
        for entry in files:
            if not entry.endswith(".yml"):
                continue
            if entry.startswith("/"):
                path = entry
            else:
                path = os.path.join(dirpath, entry)

            LOG.debug("Loading config file %s.", path)
            with open(path, "r") as yaml_file:
                config = yaml.load(yaml_file)
            update(configs, config)

        return configs

    def _save_config(self, name, params):
        """Save a copy of the current config."""
        yaml = YAML(typ="safe", pure=True)
        path = os.path.join(
            self.midascfg["PATHS"]["output_prefix"], f"{name}_cfg.yml"
        )
        # LOG.debug("Current config is %s.", params)
        params = convert(params)
        LOG.debug("Current config is %s.", params)
        LOG.info("Saving current config to %s.", path)
        with open(path, "w") as cfg_out:
            yaml.indent(mapping=4, sequence=6, offset=3)
            yaml.dump({"myconfig": params}, cfg_out)

    def _save_script(self, script):
        fname = os.path.join(
            self.midascfg["PATHS"]["output_prefix"],
            f"{self.scenario_name}_auto_script.py",
        )
        fctn = ""
        order = [
            "imports",
            "definitions",
            "simconfig",
            "sim_start",
            "model_start",
            "connects",
            "world_start",
        ]
        for part in order:
            for line in script[part]:
                fctn += line
            fctn += "\n"
        with open(fname, "w") as sfile:
            sfile.write(fctn)

    def _apply_modules(self, scenario, params):
        """Apply all required modules in the correct order."""

        LOG.debug("Creating base configuration.")
        base = import_module("midas.scenario.modules.base")
        scenario = base.configure(scenario, params, self.midascfg)

        LOG.debug("Attemp to add database.")
        database = import_module("midas.scenario.modules.database")
        database.upgrade(scenario, params)

        LOG.debug("Now adding further modules (if any).")
        for (module, clazz) in MODULES:
            # Preserve ordering of modules
            if module in params["modules"]:
                LOG.debug("Adding module %s.", module)
                mod = import_module(f"midas.scenario.modules.{module}")
                getattr(mod, clazz)().upgrade(scenario, params)

        self._apply_custom_modules(scenario, params)

        scenario["params"] = params
        scenario["script"]["definitions"].append(
            f"sensors = {scenario['sensors']}\n"
        )
        scenario["script"]["definitions"].append(
            f"actuators = {scenario['actuators']}\n"
        )
        return scenario

    def _apply_custom_modules(self, scenario, params):
        if "custom_modules" not in params:
            return
        if params["custom_modules"] is None:
            return

        LOG.debug(
            "Trying to load %d custom module(s) ...",
            len(params["custom_modules"]),
        )
        for (module, cmod) in params["custom_modules"]:
            # All custom module are loaded
            if ":" in cmod:
                mod, clazz = cmod.split(":")
            else:
                mod, clazz = cmod.rplit(".", 1)
            LOG.debug("Adding module %s.", module)
            mod = import_module(mod)
            getattr(mod, clazz)().upgrade(scenario, params)

    def _normalize(self, params):
        """Apply some auto corrections for the parameter dictionary.

        Corrects, e.g., the end definition '15*60' to 900.

        """
        for key, val in params.items():
            # Search recusively
            if isinstance(val, dict):
                self._normalize(val)

            # Correct multiplications
            if isinstance(val, str):
                if "*" in val:
                    parts = val.split("*")
                    product = 1
                    try:
                        for part in parts:
                            product *= float(part)

                        if key in ["step_size", "end"]:
                            product = int(product)
                        params[key] = product
                        LOG.debug(
                            "Corrected value for key %s (%s -> %f).",
                            key,
                            val,
                            product,
                        )
                    except ValueError:
                        # Not a multiplication
                        pass
                if val.lower() == "true":
                    val = True
                    LOG.debug(
                        "Corrected value for key %s ('true' -> bool(True)).",
                        key,
                    )
                if val.lower() == "false":
                    val = False
                    LOG.debug(
                        "Corrected value for key %s ('false' -> bool(False)).",
                        key,
                    )

            # Correct mosaik params address which is a tuple and not a list
            if key == "mosaik_params":
                if "addr" in val:
                    if isinstance(val["addr"], list):
                        LOG.debug("Corrected mosaik_params.")
                        val["addr"] = (val["addr"][0], val["addr"][1])
