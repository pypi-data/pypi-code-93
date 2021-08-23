"""
Warning:
    Experimental features are subject to breaking changes (even removals) in minor and/or patch releases.

atoti supports distributed clusters with several data cubes and one query cube.

This is not the same as a query session: in a query session, the query cube connects to a remote data cube and query its content, while in a distributed setup, multiple data cubes can join a distributed cluster where a distributed cube can be queried to retrieve the union of their data.

Distributed cubes can be used like this::

    import atoti as tt

    distributed_session = tt.experimental.create_distributed_session("dist-test")

    # The distributed cube's structure is the same as that of the data cubes that joined its cluster.
    # As a result:
    #   - the distributed cube's measures, hierarchies, and levels cannot be modified by the user
    #   - all the data cubes in the cluster must have the same measures, hierarchies, and levels
    distributed_cube = distributed_session.create_cube("DistributedCube")
    l, m = distributed_cube.levels, distributed_cube.measures

    # Create the local cube and join the distributed cluster
    session = tt.create_session()

    sales_table = session.read_csv("data/sales.csv", keys=["Sale ID"])
    cube = session.create_cube(sales_table, "sales1")

    tt.experimental.join_distributed_cluster(cube, f"http://localhost:{distributed_session.port}", "DistributedCube")

    # The distributed cube can be queried as usual, with `distributed_session.visualize()`, or `distributed_cube.query()` returning a pandas DataFrame.

    # Wait for the distributed cube to register the arrival of the data cube
    import time

    while "Amount.SUM" not in m:
        time.sleep(1)

    distributed_cube.query(m["Amount.SUM"], m["Quantity.SUM"], levels=[l["Product"]])

"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from ...cube import Cube


def create_distributed_session(
    name: str = "Unnamed", *, config: Optional[Mapping[str, Any]] = None, **kwargs: Any
):
    """Create a distributed session.

    Args:
        name: The name of the session.
        config: The configuration of the session or the path to a configuration file.
    """
    from ... import sessions

    return sessions._create_distributed_session(name, config=config, **kwargs)


def join_distributed_cluster(
    *,
    cube: Cube,
    distributed_session_url: str,
    distributed_cube_name: str,
):
    """Join the distributed cluster at the given address for the given distributed cube."""
    cube._join_distributed_cluster(distributed_session_url, distributed_cube_name)
