#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
import logging
import typing as t
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from dask.delayed import Delayed
from typing_extensions import Literal

from pyxel.calibration import (
    Algorithm,
    CalibrationMode,
    DaskBFE,
    DaskIsland,
    Island,
    MyArchipelago,
    ResultType,
)
from pyxel.calibration.fitting import ModelFitting
from pyxel.parametric.parameter_values import ParameterValues
from pyxel.pipelines import ModelFunction, Processor

try:
    import pygmo as pg

    WITH_PYGMO: bool = True
except ImportError:
    WITH_PYGMO = False

if t.TYPE_CHECKING:
    from ..inputs_outputs import CalibrationOutputs


def to_path_list(values: t.Sequence[t.Union[str, Path]]) -> t.List[Path]:
    """TBW."""
    return [Path(obj).resolve() for obj in values]


class Calibration:
    """TBW."""

    def __init__(
        self,
        outputs: "CalibrationOutputs",
        output_dir: t.Optional[Path] = None,
        fitting: t.Optional[ModelFitting] = None,
        mode: Literal["pipeline", "single_model"] = "pipeline",
        result_type: Literal["image", "signal", "pixel"] = "image",
        result_fit_range: t.Optional[t.Sequence[int]] = None,
        result_input_arguments: t.Optional[t.Sequence[ParameterValues]] = None,
        target_data_path: t.Optional[t.Sequence[Path]] = None,
        target_fit_range: t.Optional[t.Sequence[int]] = None,
        fitness_function: t.Optional[ModelFunction] = None,
        algorithm: t.Optional[Algorithm] = None,
        parameters: t.Optional[t.Sequence[ParameterValues]] = None,
        seed: t.Optional[int] = None,
        num_islands: int = 1,
        num_evolutions: int = 1,
        num_best_decisions: t.Optional[int] = None,
        topology: Literal["unconnected", "ring", "fully_connected"] = "unconnected",
        type_islands: Literal[
            "multiprocessing", "multithreading", "ipyparallel"
        ] = "multiprocessing",
        weighting_path: t.Optional[t.Sequence[Path]] = None,
    ):
        if not WITH_PYGMO:
            raise ImportError(
                "Missing optional package 'pygmo'.\n"
                "Please install it with 'pip install pyxel-sim[calibration]' "
                "or 'pip install pyxel-sim[all]'"
            )

        if seed is not None and seed not in range(100001):
            raise ValueError("'seed' must be between 0 and 100000.")

        if num_islands < 1:
            raise ValueError("'num_islands' must superior or equal to 1.")

        self._log = logging.getLogger(__name__)

        self.outputs = outputs

        self._output_dir = output_dir  # type:t.Optional[Path]
        self._fitting = fitting  # type: t.Optional[ModelFitting]

        self._calibration_mode = CalibrationMode(mode)

        self._result_type = ResultType(result_type)  # type: ResultType

        self._result_fit_range = (
            result_fit_range if result_fit_range else []
        )  # type: t.Sequence[int]

        self._result_input_arguments = (
            result_input_arguments if result_input_arguments else []
        )  # type: t.Sequence[ParameterValues]

        self._target_data_path = (
            to_path_list(target_data_path) if target_data_path else []
        )  # type: t.Sequence[Path]
        self._target_fit_range = (
            target_fit_range if target_fit_range else []
        )  # type: t.Sequence[int]

        self._fitness_function = fitness_function  # type: t.Optional[ModelFunction]
        self._algorithm = algorithm  # type: t.Optional[Algorithm]

        self._parameters = (
            parameters if parameters else []
        )  # type: t.Sequence[ParameterValues]

        self._seed = np.random.randint(0, 100000) if seed is None else seed  # type: int

        self._num_islands = num_islands  # type: int
        self._num_evolutions = num_evolutions  # type: int
        self._num_best_decisions = num_best_decisions  # type: t.Optional[int]
        self._type_islands = Island(type_islands)  # type:Island
        self._topology = (
            topology
        )  # type: t.Literal['unconnected', 'ring', 'fully_connected']

        self._weighting_path = weighting_path  # type: t.Optional[t.Sequence[Path]]

    @property
    def output_dir(self) -> Path:
        """TBW."""
        if not self._output_dir:
            raise RuntimeError("No 'output_dir' defined !")

        return self._output_dir

    @output_dir.setter
    def output_dir(self, value: Path) -> None:
        """TBW."""
        self._output_dir = value

    @property
    def fitting(self) -> ModelFitting:
        """TBW."""
        if not self._fitting:
            raise RuntimeError("No 'fitting' defined !")

        return self._fitting

    @fitting.setter
    def fitting(self, value: ModelFitting) -> None:
        """TBW."""
        self._fitting = value

    @property
    def calibration_mode(self) -> CalibrationMode:
        """TBW."""
        return self._calibration_mode

    @calibration_mode.setter
    def calibration_mode(self, value: CalibrationMode) -> None:
        """TBW."""
        self._calibration_mode = value

    @property
    def result_type(self) -> ResultType:
        """TBW."""
        return self._result_type

    @result_type.setter
    def result_type(self, value: ResultType) -> None:
        """TBW."""
        self._result_type = value

    @property
    def result_fit_range(self) -> t.Sequence[int]:
        """TBW."""
        return self._result_fit_range

    @result_fit_range.setter
    def result_fit_range(self, value: t.Sequence[int]) -> None:
        """TBW."""
        self._result_fit_range = value

    @property
    def result_input_arguments(self) -> t.Sequence[ParameterValues]:
        """TBW."""
        return self._result_input_arguments

    @result_input_arguments.setter
    def result_input_arguments(self, value: t.Sequence[ParameterValues]) -> None:
        """TBW."""
        self._result_input_arguments = value

    @property
    def target_data_path(self) -> t.Sequence[Path]:
        """TBW."""
        return self._target_data_path

    @target_data_path.setter
    def target_data_path(self, value: t.Sequence[Path]) -> None:
        """TBW."""
        self._target_data_path = value

    @property
    def target_fit_range(self) -> t.Sequence[int]:
        """TBW."""
        return self._target_fit_range

    @target_fit_range.setter
    def target_fit_range(self, value: t.Sequence[int]) -> None:
        """TBW."""
        self._target_fit_range = value

    @property
    def fitness_function(self) -> ModelFunction:
        """TBW."""
        if not self._fitness_function:
            raise RuntimeError("No 'fitness_function' defined !")

        return self._fitness_function

    @fitness_function.setter
    def fitness_function(self, value: ModelFunction) -> None:
        """TBW."""
        self._fitness_function = value

    @property
    def algorithm(self) -> Algorithm:
        """TBW."""
        if not self._algorithm:
            raise RuntimeError("No 'algorithm' defined !")

        return self._algorithm

    @algorithm.setter
    def algorithm(self, value: Algorithm) -> None:
        """TBW."""
        self._algorithm = value

    @property
    def parameters(self) -> t.Sequence[ParameterValues]:
        """TBW."""
        return self._parameters

    @parameters.setter
    def parameters(self, value: t.Sequence[ParameterValues]) -> None:
        """TBW."""
        self._parameters = value

    @property
    def seed(self) -> int:
        """TBW."""
        return self._seed

    @seed.setter
    def seed(self, value: int) -> None:
        """TBW."""
        if value not in range(100001):
            raise ValueError("'seed' must be between 0 and 100000.")

        self._seed = value

    @property
    def num_islands(self) -> int:
        """TBW."""
        return self._num_islands

    @num_islands.setter
    def num_islands(self, value: int) -> None:
        """TBW."""
        if value < 1:
            raise ValueError("'num_islands' must superior or equal to 1.")

        self._num_islands = value

    @property
    def num_evolutions(self) -> int:
        """TBW."""
        return self._num_evolutions

    @num_evolutions.setter
    def num_evolutions(self, value: int) -> None:
        """TBW."""
        self._num_evolutions = value

    @property
    def num_best_decisions(self) -> t.Optional[int]:
        """TBW."""
        return self._num_best_decisions

    @num_best_decisions.setter
    def num_best_decisions(self, value: t.Optional[int]) -> None:
        """TBW."""
        if isinstance(value, int) and value < 0:
            raise ValueError(
                "'num_best_decisions' must be 'None' or a positive integer"
            )

        self._num_best_decisions = value

    @property
    def topology(self) -> Literal["unconnected", "ring", "fully_connected"]:
        """TBW."""
        return self._topology

    @topology.setter
    def topology(self, value: t.Any) -> None:
        if value not in ["unconnected", "ring", "fully_connected"]:
            raise ValueError(
                "Expecting value: 'unconnected', 'ring' or 'fully_connected'"
            )

        self._topology = value

    @property
    def weighting_path(self) -> t.Optional[t.Sequence[Path]]:
        """TBW."""
        return self._weighting_path

    @weighting_path.setter
    def weighting_path(self, value: t.Sequence[Path]) -> None:
        """TBW."""
        self._weighting_path = value

    def run_calibration(
        self,
        processor: Processor,
        output_dir: Path,
        with_progress_bar: bool = True,
    ) -> t.Tuple[xr.Dataset, pd.DataFrame, pd.DataFrame]:
        """Run calibration pipeline."""
        pg.set_global_rng_seed(seed=self.seed)
        self._log.info("Seed: %d", self.seed)

        self.output_dir = output_dir

        self.fitting = ModelFitting(processor=processor, variables=self.parameters)
        self.fitting.configure(
            calibration_mode=self.calibration_mode,
            generations=self.algorithm.generations,
            population_size=self.algorithm.population_size,
            simulation_output=self.result_type,
            fitness_func=self.fitness_function,
            target_output=self.target_data_path,
            target_fit_range=self.target_fit_range,
            out_fit_range=self.result_fit_range,
            input_arguments=self.result_input_arguments,
            weighting=self.weighting_path,
            file_path=output_dir,
        )

        if self.num_islands > 1:  # default
            # Create an archipelago
            user_defined_island = DaskIsland()
            user_defined_bfe = DaskBFE()

            if self.topology == "unconnected":
                topo = pg.unconnected()
            elif self.topology == "ring":
                topo = pg.ring()
            elif self.topology == "fully_connected":
                topo = pg.fully_connected()
            else:
                raise NotImplementedError(f"topology {self.topology!r}")

            # Create a new archipelago
            # This operation takes some time ...
            my_archipelago = MyArchipelago(
                num_islands=self.num_islands,
                udi=user_defined_island,
                algorithm=self.algorithm,
                problem=self.fitting,
                pop_size=self.algorithm.population_size,
                bfe=user_defined_bfe,
                topology=topo,
                seed=self.seed,
                with_bar=with_progress_bar,
            )

            # Run several evolutions in the archipelago
            ds, df_processors, df_all_logs = my_archipelago.run_evolve(
                num_evolutions=self._num_evolutions,
                num_best_decisions=self._num_best_decisions,
            )

            ds.attrs["topology"] = self.topology
            ds.attrs["result_type"] = str(self.fitting.sim_output)

        else:
            raise NotImplementedError("Not implemented for 1 island.")

        self._log.info("Calibration ended.")
        return ds, df_processors, df_all_logs

    # TODO: This function must be improved
    # TODO: Speed-up this function
    # def old_post_processing(
    #     self,
    #     calib_results: t.Sequence[CalibrationResult],
    #     output: "CalibrationOutputs",
    # ) -> None:
    #     """TBW."""
    #     for one_calib_result in tqdm(calib_results):  # type: CalibrationResult
    #
    #         # TODO: Create a new method in output called '.save_processor(processor)'
    #         output.calibration_outputs(processor_list=one_calib_result.processors)
    #
    #         for idx, (processor, target_data) in enumerate(
    #             zip(one_calib_result.processors, self.fitting.all_target_data)
    #         ):
    #             simulated_data = self.fitting.get_simulated_data(
    #                 processor
    #             )  # type: np.ndarray
    #             output.fitting_plot(
    #                 target_data=target_data, simulated_data=simulated_data, data_i=idx
    #             )
    #
    #         output.fitting_plot_close(
    #             result_type=self.result_type, island=one_calib_result.island
    #         )
    #
    #     first_calib_result = calib_results[0]  # type: CalibrationResult
    #     output.calibration_plots(
    #         results=first_calib_result.results, fitness=first_calib_result.fitness
    #     )

    def post_processing(
        self,
        ds: xr.Dataset,
        df_processors: pd.DataFrame,
        output: "CalibrationOutputs",
    ) -> t.Sequence[Delayed]:
        """TBW."""
        filenames = output.save_processors(
            processors=df_processors
        )  # type: t.Sequence[Delayed]

        # TODO: Use output.fitting_plot ?
        # TODO: Use output.fitting_plot_close ?
        # TODO: Use output.calibration_plots ?

        return filenames
