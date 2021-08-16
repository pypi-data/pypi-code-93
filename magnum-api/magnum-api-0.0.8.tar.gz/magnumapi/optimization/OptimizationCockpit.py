from time import sleep

import pandas as pd
from IPython.display import display, clear_output

from magnumapi.optimization.GeneticOptimization import RoxieGeneticOptimization
from magnumapi.optimization.OptimizationCockpitWidget import OptimizationCockpitWidget


class OptimizationCockpit:

    def __init__(self, logger_abs_path, config, optim_input_df, block_inputs, cadata) -> None:
        self.gen_opt = RoxieGeneticOptimization(config=config, optim_input_df=optim_input_df)
        self.logger_abs_path = logger_abs_path
        self.config = config
        self.optim_input_df = optim_input_df
        self.block_inputs = block_inputs
        self.cadata = cadata

    def display(self, t_sleep_in_sec=100.0) -> None:
        logger_df = pd.read_csv(self.logger_abs_path, index_col=0)
        if len(logger_df):
            widget = OptimizationCockpitWidget(self.gen_opt,
                                               logger_df,
                                               self.config,
                                               self.optim_input_df,
                                               self.block_inputs,
                                               self.cadata)
            widget.build()
            display(widget.show())

        while True:
            sleep(t_sleep_in_sec)

            logger_new_df = pd.read_csv(self.logger_abs_path, index_col=0)
            if len(logger_new_df) > len(logger_df):
                widget = OptimizationCockpitWidget(self.gen_opt,
                                                   logger_df,
                                                   self.config,
                                                   self.optim_input_df,
                                                   self.block_inputs,
                                                   self.cadata)
                widget.build()
                clear_output()
                display(widget.show())
