from dataclasses import dataclass
from typing import List

from magnumapi.optimization.ObjectiveConfig import ObjectiveConfig
from magnumapi.optimization.OptimizationNotebookConfig import OptimizationNotebookConfig


@dataclass
class OptimizationConfig:
    input_folder: str
    output_folder: str
    logger_rel_path: str
    n_pop: int
    n_gen: int
    r_cross: float
    r_mut: float
    objectives: List[ObjectiveConfig]
    notebooks: List[OptimizationNotebookConfig]

    def __str__(self):
        notebooks_str = "\n\n".join(str(notebook) for notebook in self.notebooks)
        objectives_str = "\n\n".join(str(objective) for objective in self.objectives)
        return "input_folder: %s\n" \
               "output_folder: %s\n" \
               "logger_rel_path: %s\n" \
               "n_pop: %d\n" \
               "n_gen: %d\n" \
               "r_cross: %f\n" \
               "r_mut: %f\n" \
               "objectives: \n\n" \
               "%snotebooks: \n\n" \
               "%s" % (self.input_folder,
                       self.output_folder,
                       self.logger_rel_path,
                       self.n_pop,
                       self.n_gen,
                       self.r_cross,
                       self.r_mut,
                       objectives_str,
                       notebooks_str)
