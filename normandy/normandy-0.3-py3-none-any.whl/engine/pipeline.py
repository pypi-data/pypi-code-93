
class pipeline:
    # Main class - Is in charge od the orchestry of processes.

    from datetime import datetime
    from multiprocessing import Pool
    from normandy.engine.logger import main_logger, logger

    def __init__(self, env, tags, global_params, log_level, threads):
        from yaml import load
        from yaml.loader import SafeLoader

        self.tags = set(tags)
        with open("pipeline/pipeline_conf.yml") as file:
            confs = load(file, Loader=SafeLoader)

            # Define flows with the givens tags
            self.__flows__ = [flow(data, flow_name, self.tags, global_params) for flow_name, data in confs["flows"].items() if self.tags.intersection(set(data["tags"]))]

            # Read the project configurations
            self.__confs__ = confs["confs"]
            self.__confs__["active_env"] = env
            if log_level != None:
                self.__log_level__ = log_level
            elif "log_level" in confs["confs"].keys():
                self.__log_level__ = confs["confs"]["log_level"]
            else:
                self.__log_level__ = "info"
            if threads != None:
                self.__threads__ = threads
            elif "threads" in confs["confs"].keys():
                self.__threads__ = confs["confs"]["threads"]
            else:
                self.__threads__ = 8

    def get_path(self):
        # Return the project path
        return self.__confs__['path']

    def get_env_confs(self):
        # Return the active enviroment configurations
        return self.__confs__["envs"][self.__confs__["active_env"]]

    def __step_runner__(self, step):
        # Run each step using parallel processing over each process.
        _t = self.datetime.now()
        log = self.logger(step, self.__log_level__)
        with self.Pool(min(step.processes_number(), self.__threads__)) as pool:
            try:
                pool.map(self.__process_runner__, step.processes())
            except Exception as e:
                log.error(e)
                raise e
        log.info(f"Step successfully ended at {self.datetime.now()} - Step time: {self.datetime.now() - _t}")

    def __process_runner__(self, process):
        # Run the selected process
        process.execute(self)

    def __flow_runner__(self, flow):
        # Run the defined data flow, step by step

        _t = self.datetime.now()
        log = self.main_logger(flow, self.__log_level__)

        for step in flow.steps():
            try:
                self.__step_runner__(step)
            except Exception as e:
                log.error(e)
                raise e
        log.write(f"flow successfully ended at {self.datetime.now()} - Flow time: {self.datetime.now() - _t}")

    def start_pipeline(self):
        # Execute the pipeline
        for fl in self.__flows__:
            self.__flow_runner__(fl)

class flow:

    def __init__(self, flow_data, name, tags, global_params):
        self.__type__ = "flow"
        self.__tags__ = flow_data["tags"]
        if global_params == None:
            self.__params__ = flow_data["params"] if "params" in flow_data.keys() else None
        else:
            if not "params" in flow_data.keys():
                flow_data["params"] = {}
            for param_name, param_value in global_params:
                flow_data["params"][param_name] = param_value
            self.__params__ = flow_data["params"]

        self.__name__ = name
        self.__steps__ = [step(data, step_name, self.__name__, tags, self.__params__) for step_name, data in flow_data["steps"].items()]

    def steps(self):
        return self.__steps__

    def step_number(self):
        return len(self.__steps__)

    def __str__(self):
        return f"Flow: {self.__name__}"

class step:

    def __init__(self, step_data, name, belong, tags, global_params):

        from normandy.engine.errors import definition_error

        self.__type__ = "step"
        self.__name__ = name
        self.__from_flow__ = belong
        try:
            if type(step_data) == dict:
                self.__parse_processes__(step_data, tags, global_params)
            else:
                process_data = {"params": global_params}
                self.__processes__ = [process(process_data, process_name, self.__name__, self.__from_flow__) for process_name in step_data]
        except Exception as e:
            raise definition_error(f"Bad process definition: {e}")

    def __parse_processes__(self, step_data, tags, global_params):
        self.__processes__ = []
        for process_name, process_data in step_data.items():
            if type(process_data) == dict and "avoid_tags" in process_data.keys() and tags.intersection(set(process_data["avoid_tags"])):
                continue
            # set global params
            if not "params" in process_data.keys():
                process_data["params"] = global_params
            elif not global_params == None:
                for param in global_params.keys():
                    if param in process_data["params"]:
                        continue
                    process_data["params"][param] = global_params[param]

            if type(process_data) == dict and "iter_param" in process_data.keys():
                param_name = process_data["iter_param"]["name"]

                for param_value in process_data["iter_param"]["values"]:
                    process_data["params"] = process_data["params"].copy()
                    process_data["params"][param_name] = param_value
                    self.__processes__.append(process(process_data, process_name, self.__name__, self.__from_flow__))
            else:
                self.__processes__.append(process(process_data, process_name, self.__name__, self.__from_flow__))


    def processes(self):
        return self.__processes__

    def processes_number(self):
        return len(self.__processes__)

    def __str__(self):
        return f"Step from {self.__from_flow__} flow: {self.__name__}"

class process:

    def __init__(self, process_data, name, step_name, flow_name):

        self.__type__ = "process"
        self.__name__ = name
        self.__from_step__ = step_name
        self.__from_flow__ = flow_name
        self.__error_tolerance__ = self.__setup__(process_data, "error_tolerance")
        self.__params__ = self.__setup__(process_data, "params")

    def __setup__(self, data, setup):
        setups_defaults = {
            "error_tolerance" : False,
            "params" : {}
        }
        if type(data) == dict and setup in data.keys():
            return data[setup]
        return setups_defaults[setup]

    def execute(self, pipe):
        from datetime import datetime
        from importlib.util import spec_from_file_location, module_from_spec
        from normandy.engine.errors import process_error
        from normandy.engine.logger import logger

        _t = datetime.now()
        log = logger(self, pipe.__log_level__)

        # Import and execute the user define module
        spec = spec_from_file_location(f"{self.__from_step__}.{self.__name__}", f"{pipe.get_path()}/pipeline/{self.__from_step__}/{self.__name__}.py")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        try:
            module.process(pipe, log, self.__params__)
        except Exception as e:
            if not self.__error_tolerance__:
                raise process_error("Process exception without errors tolerance")
            log.error(e)

        log.info(f"Process successfully ended at {datetime.now()} - Process time: {datetime.now() - _t}")
        return

    def __str__(self):
        return f"Process from {self.__from_step__} step from {self.__from_flow__} flow: {self.__name__} -- Params: {self.__params__}"
