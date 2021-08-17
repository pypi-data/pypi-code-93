# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Callable, Dict, List, Optional

from azureml.train.automl.runtime._dask.mpi_dask_cluster import MpiDaskClsuter


class DaskJob:

    @staticmethod
    def run(
            driver_func: Callable[..., Any],
            driver_func_args: List[Optional[str]] = [],
            driver_func_kwargs: Dict[str, Any] = {}) -> Any:
        """Initialize a Dask cluster and run the driver function on it."""
        cluster = MpiDaskClsuter()
        rank = cluster.start()
        try:
            # Only run the driver function on rank 0
            if rank == 0:
                return driver_func(*driver_func_args, **driver_func_kwargs)
        finally:
            if rank == 0:
                cluster.shutdown()
