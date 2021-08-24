from threading import Timer

import pandas as pd
from IPython.display import display

from magnumapi.optimization.GeneticOptimization import RoxieGeneticOptimization
from magnumapi.optimization.OptimizationCockpitWidget import OptimizationCockpitWidget


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class OptimizationCockpit:

    def __init__(self, logger_abs_path, config, optim_input_df, block_inputs, cadata) -> None:
        self.gen_opt = RoxieGeneticOptimization(config=config, optim_input_df=optim_input_df)
        self.logger_abs_path = logger_abs_path
        self.logger_df = pd.read_csv(self.logger_abs_path, index_col=0)
        self.config = config
        self.optim_input_df = optim_input_df
        self.block_inputs = block_inputs
        self.cadata = cadata
        self.widget = None

    def display(self, t_sleep_in_sec=5.0) -> None:

        if len(self.logger_df):
            self.widget = OptimizationCockpitWidget(self.gen_opt,
                                                    self.logger_df,
                                                    self.config,
                                                    self.optim_input_df,
                                                    self.block_inputs,
                                                    self.cadata)

            self.widget.build()
            display(self.widget.show())

            RepeatedTimer(t_sleep_in_sec, self.update_cockpit)

    def update_cockpit(self):
        logger_new_df = pd.read_csv(self.logger_abs_path, index_col=0)
        if len(logger_new_df) > len(self.logger_df):
            self.logger_df = logger_new_df
            self.widget.min_logger_df = self.widget.gen_opt.get_min_fitness_per_generation(self.logger_df)
            self.widget.widget.data = []
            self.widget.build()
