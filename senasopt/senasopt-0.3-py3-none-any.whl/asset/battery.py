# -*- coding: utf-8 -*-
"""
Functions related to modelling of batteries.

This file can also be imported as a module and contains the following
functions:


References:
    [1] J. Twidell & T. Weir, Renewable Energy Resources, 2nd edition, 
    Taylor and Francis, 2006

"""

# Import all useful libraries
import casadi as ca
import casadi.tools
import numpy as np

from .optimise import runge_kuta, solve_optimisation, extract_optimisation_results


class Battery:
    def __init__(
        self,
        capacity=10,
        rated_power=2,
        charge_efficiency=0.98,
        discharge_efficiency=0.98,
        connection_sizing=np.inf,
    ):
        """Creates a battery object

        Parameters
        ----------
        capacity : float
            Capacity of the battery [kWh]
            Default : 10

        rated_power : float
            Rated power of the inverter [kW]
            Default : 2

        charge_efficiency : float
            Efficiency of the battery charging [0-1]
            Default : 0.98

        discharge_efficiency : float
            Efficiency of the battery discharging [0-1]
            Default : 0.98

        connection_sizing : float
            Sizing of the grid connection point [kW] (use inf to ignore)
            Default : numpy.inf

        """
        self.__model = _battery_model(
            capacity=capacity,
            rated_power=rated_power,
            charge_efficiency=charge_efficiency,
            discharge_efficiency=discharge_efficiency,
            connection_sizing=connection_sizing,
        )
        self.set_state(0)

    def set_state(self, soc):
        """Sets the state of charge of the battery

        Parameters
        ----------
        soc : float
            New state of charge of the the building
        """
        self.__state = soc

    def optimal_schedule(self, data):
        """Solves an optimal scheduling problem.

        Parameters
        ----------
        data : pandas.DataFrame
            Data for the optimisation : [power_price,local_demand,local_production]
            Data for the optimisation : [power_price_import,power_price_export,local_demand,local_production]

        Returns
        -------
        performance : dict(float)
            Performance indicators (revenue,energy_output,energy_intake,energy_losses,energy_export,energy_import)

        timeseries : pandas.DataFrame
            Dataframe with inputs and outputs of optimisation
        """
        performance, timeseries = _battery_optimal_controller(
            data,
            model=self.__model,
            initial_state=self.__state,
        )
        return performance, timeseries


def _battery_model(
    capacity=1e4,
    rated_power=1e3,
    charge_efficiency=0.98,
    discharge_efficiency=0.98,
    connection_sizing=np.inf,
):

    # State vector
    fields_x = ["state_of_charge"]
    x = ca.tools.struct_symMX(fields_x)

    # Input vector
    fields_u = ["battery_power_intake", "battery_power_output"]
    u = ca.tools.struct_symMX(fields_u)

    # Disturbance vector (none for now)
    fields_v = ["None"]
    v = ca.tools.struct_symMX(fields_v)

    # State equations
    dxdt = ca.tools.struct_MX(x)
    dxdt["state_of_charge"] = (
        charge_efficiency * u["battery_power_intake"]
        - u["battery_power_output"] / discharge_efficiency
    )

    # ODE Right-hand side
    f = ca.Function("f", [x, u, v], [dxdt], ["x", "u", "v"], ["dx/dt"])

    # Single step time propagation
    dt = ca.MX.sym("dt")
    F_SSM = runge_kuta(f, x, u, v, dt, order=4)

    model = {
        "SSM": F_SSM,
        "x0_shape": 1,
        "u": u,
        "v": v,
        "x": x,
        "data_fields": {
            "u": fields_u,
            "v": fields_v,
            "x": fields_x,
        },
        "performance_fields": {
            "energy": "Php",
            "indoor_temperature": "Tr",
        },
        "constraints": {
            "u_min": 0,
            "u_max": rated_power,
            "x_min": 0,
            "x_max": capacity,
            "connection_sizing": connection_sizing,
        },
    }

    return model


def _battery_optimal_controller(
    data,
    model=_battery_model(),
    initial_state=0,
):
    # Input data=[power_price,local_demand,local_production]

    # Converting for usage of hour time units
    dt_index = data.index[1:-1] - data.index[0:-2]
    dt_data = (dt_index.to_numpy() / np.timedelta64(1, "h")).mean()
    N = len(data)

    # Price is usually given in unit/kWh
    if "power_price" in data.keys():
        columns2keep = ["power_price"]
        import_column = "power_price"
        export_column = "power_price"
    elif ("power_price_import" in data.keys()) and (
        "power_price_export" in data.keys()
    ):
        columns2keep = ["power_price_import", "power_price_export"]
        import_column = "power_price_import"
        export_column = "power_price_export"
    else:
        raise Exception("Illegal price specification")

    power_price_import = data[import_column].to_numpy()
    power_price_export = data[export_column].to_numpy()

    if "local_demand" in data.keys():
        local_demand = data["local_demand"].to_numpy().reshape(1, N)
    else:
        local_demand = np.zeros(N).reshape(1, N)

    if "local_production" in data.keys():
        local_production = data["local_production"].to_numpy().reshape(1, N)
    else:
        local_production = np.zeros(N).reshape(1, N)

    ## ----------- System description -------------------

    F_SSM = model["SSM"]
    u = model["u"]
    v = model["v"]
    x = model["x"]
    x0 = initial_state
    fields_u = model["data_fields"]["u"]
    fields_v = model["data_fields"]["v"]
    fields_x = model["data_fields"]["x"]

    field_perf_energy = model["performance_fields"]["energy"]
    field_perf_Ti = model["performance_fields"]["indoor_temperature"]

    V = np.zeros(N).reshape(1, N)

    ## ----------- Optimal control -------------------
    # Optimization horizon
    N = len(data)
    opti = ca.Opti()

    # Decision variables for states and inputs
    X = opti.variable(x.size, N + 1)
    U = opti.variable(u.size, N)

    # Computing imports and exports
    fields_u = ["battery_power_intake", "battery_power_output"]
    Pin_battery = U[0, :]
    Pout_battery = U[1, :]
    y_net_export = (Pout_battery + local_production) - (Pin_battery + local_demand)
    y_Pimport = ca.fmax(0, -y_net_export)
    y_Pexport = ca.fmax(0, y_net_export)

    # Initial state is a parameter
    x_min = model["constraints"]["x_min"]
    x_max = model["constraints"]["x_max"]
    u_min = model["constraints"]["u_min"]
    u_max = model["constraints"]["u_max"]

    opti.subject_to(X[:, 0] == x0)
    opti.subject_to(X[0, :] <= x_max)
    opti.subject_to(X[0, :] >= x_min)

    opti.subject_to(U[0, :] <= u_max)
    opti.subject_to(U[0, :] >= u_min)
    opti.subject_to(U[1, :] <= u_max)
    opti.subject_to(U[1, :] >= u_min)

    # State constraints
    for k in range(N):
        opti.subject_to(X[:, k + 1] == F_SSM(X[:, k], U[:, k], V[:, k], dt_data))

    transformer_sizing = model["constraints"]["connection_sizing"]
    if np.isinf(transformer_sizing) is False:
        opti.subject_to(y_Pimport <= transformer_sizing)
        opti.subject_to(y_Pexport <= transformer_sizing)

    # Objectives
    cost = ca.mtimes(y_Pimport, power_price_import) - ca.mtimes(
        y_Pexport, power_price_export
    )
    opti.minimize(cost)

    # Solve the optimisation
    sol = solve_optimisation(problem=opti, solver="ipopt", verbose=False)

    # Structuring outputs
    val_Pout = sol.value(Pout_battery)
    val_Pin = sol.value(Pin_battery)
    val_revenue = -sol.value(cost)
    val_export = sol.value(y_Pexport)
    val_import = sol.value(y_Pimport)

    performance = dict(
        revenue=np.sum(val_revenue),
        energy_output=np.sum(val_Pout),
        energy_intake=np.sum(val_Pin),
        energy_losses=np.sum(val_Pin) - np.sum(val_Pout),
        energy_export=np.sum(val_export),
        energy_import=np.sum(val_import),
    )

    timeseries = extract_optimisation_results(
        solution=sol, model=model, data=data, X=X, U=U, V=V, keep=columns2keep
    )
    # timeseries["battery_power_intake"] = sol.value(val_Pin)
    # timeseries["battery_power_output"] = sol.value(val_Pout)
    timeseries["power_import"] = sol.value(val_import)
    timeseries["power_export"] = sol.value(val_export)
    timeseries["power_import"] = sol.value(val_import)
    timeseries["revenue"] = (
        timeseries["power_export"] * timeseries[export_column]
        - timeseries["power_import"] * timeseries[import_column]
    )

    return performance, timeseries
