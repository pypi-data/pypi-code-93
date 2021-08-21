# -*- coding: utf-8 -*-
"""
Functions related to modelling of buildings.

This file can also be imported as a module and contains the following
functions:


References:
    [1] P.J.C. Vogler-Finck, Forecast and control of heating loads in receding horizon, 
    Ph.D. thesis, Aalborg University, 2018

    [2] R. Halvgaard, Model Predictive Control for Smart Energy Systems,
    Ph.D. thesis, DTU Compute, 2014

"""

# Import all useful libraries
import casadi as ca
import casadi.tools
import numpy as np

from .optimise import extract_optimisation_results, runge_kuta, solve_optimisation


class HouseholdHeatPump:
    def __init__(self, house_type):
        """Creates an instance of building with heat-pump

        Parameters
        ----------
        house_type : str
            Type of archetype ("modern" or "low_energy")

        OBS: The two archetypes have different state space representations
        """
        self.__house_type = house_type
        self.__model = _household_heat_pump_model(house_type=house_type)
        self.set_state(20 * self.__model["x0_shape"])

    def set_state(self, temperature_state):
        """Sets the state of the building

        Parameters
        ----------
        temperature_state : numpy.array
            New state of the building
            (if unsure, check the size of self.__model["x0_shape"])
        """
        if len(temperature_state) != len(self.__model["x0_shape"]):
            raise Exception(
                "Inconsistent length for the state vector (should be {})".format(
                    self.__model["x0_shape"]
                )
            )

        self.__state = temperature_state

    def optimal_schedule(self, data):
        """Solves an optimal scheduling problem.

        Parameters
        ----------
        data : pandas.DataFrame
            Data for the optimisation : ["solar_irradiance","ambient_temperature","power_price"]

        Returns
        -------
        performance : dict(float)
            Performance indicators (energy_demand,Ti_cold,Ti_hot)

        timeseries : pandas.DataFrame
            Dataframe with inputs and outputs of optimisation
        """
        performance, timeseries = _household_heat_pump_optimal_controller(
            data, model=self.__model, initial_state=self.__state
        )
        return performance, timeseries


def _household_heat_pump_model(house_type="low_energy"):

    kJpK_2_kWhpK = 1 / 3600
    kJpKh_2_kWpK = 1 / 3600
    pkW_2_pW = 1 / 1000

    # Units:
    # Cx in kWh/K
    # UAxx in kW/K
    # Power in kW
    if house_type == "low_energy":
        Cr = 810 * kJpK_2_kWhpK
        Cf = 3315 * kJpK_2_kWhpK
        Cw = 836 * kJpK_2_kWhpK
        UAra = 28 * kJpKh_2_kWpK
        UAfr = 624 * kJpKh_2_kWpK
        UAwf = 28 * kJpKh_2_kWpK
        As = (
            4.641 * pkW_2_pW
        )  # Assuming the same as in the other house, as missing from [2]
        COP = 3
        rated_power = 2

    elif house_type == "modern":
        Cr = 3631 * kJpK_2_kWhpK
        Cf = 10031 * kJpK_2_kWhpK
        Ce = 1171 * kJpK_2_kWhpK
        Cw = (
            836 * kJpK_2_kWhpK
        )  # Assuming the same as in the other house, as missing from [2]
        UAra = 243.7 * kJpKh_2_kWpK
        UAfr = 1840 * kJpKh_2_kWpK
        UAwf = 243.7 * kJpKh_2_kWpK
        As = 4.641 * pkW_2_pW
        COP = 3
        rated_power = 2

    else:
        raise Exception("Illegal house_type ({})".format(house_type))

    # State vector
    if house_type == "low_energy":
        fields_x = ["Tr", "Tf", "Tw"]
    elif house_type == "modern":
        fields_x = ["Tr", "Te", "Tf", "Tw"]
    else:
        raise Exception("Illegal house_type ({})".format(house_type))

    x = ca.tools.struct_symMX(fields_x)

    # Input vector
    fields_u = ["Php"]
    u = ca.tools.struct_symMX(fields_u)

    # Disturbance vector
    fields_v = ["solar_irradiance", "ambient_temperature"]
    v = ca.tools.struct_symMX(fields_v)

    # State equations
    dxdt = ca.tools.struct_MX(x)
    Ti0 = 1

    if house_type == "low_energy":
        dxdt["Tr"] = (
            (x["Tf"] - x["Tr"]) * UAfr
            + (v["ambient_temperature"] - x["Tr"]) * UAra
            + As * v["solar_irradiance"]
        ) / Cr
        dxdt["Tf"] = ((x["Tr"] - x["Tf"]) * UAfr + (x["Tw"] - x["Tf"]) * UAwf) / Cf
        dxdt["Tw"] = ((x["Tf"] - x["Tw"]) * UAwf + COP * u["Php"]) / Cw
        x0 = np.array([Ti0, Ti0, Ti0])

    elif house_type == "modern":
        dxdt["Tr"] = (
            (x["Te"] - x["Tr"]) * (UAra * 2)
            + (x["Tf"] - x["Tr"]) * UAfr
            + As * v["solar_irradiance"]
        ) / Cr
        dxdt["Te"] = (
            (v["ambient_temperature"] - x["Te"]) * (UAra * 2)
            + (x["Tr"] - x["Te"]) * UAra
        ) / Ce
        dxdt["Tf"] = ((x["Tw"] - x["Tf"]) * UAwf + (x["Tr"] - x["Tf"]) * UAfr) / Cf
        dxdt["Tw"] = ((x["Tf"] - x["Tw"]) * UAwf + COP * u["Php"]) / Cw
        x0 = np.array([Ti0, Ti0, Ti0, Ti0])

    else:
        raise Exception("Illegal house_type ({})".format(house_type))

    f = ca.Function("f", [x, u, v], [dxdt], ["x", "u", "v"], ["dx/dt"])
    dt = ca.MX.sym("dt")
    F_SSM = runge_kuta(f, x, u, v, dt, order=4)

    model = {
        "SSM": F_SSM,
        "x0_shape": x0,
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
        },
    }

    return model


def _household_heat_pump_optimal_controller(data, model, initial_state):

    # Models taken from [2]

    # Inputs:
    # data[["solar_irradiance","ambient_temperature","power_price"]]

    # Converting for usage of hour time units
    dt_data = (
        (data.index[1:-1] - data.index[0:-2]).to_numpy() / np.timedelta64(1, "h")
    ).mean()
    price = data["power_price"].to_numpy()  # Price is usually given in unit/kWh

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

    # Preferences
    Ti0 = 21
    Ti_max = 25
    Ti_setp = 22
    Ti_min = 20

    ## ----------- Optimal control -------------------
    # Optimization horizon
    N = len(data)

    opti = ca.Opti()

    # Decision variables for states and inputs
    X = opti.variable(x.size, N + 1)
    U = opti.variable(u.size, N)
    V = data[fields_v].to_numpy().transpose()

    # Initial state is a parameter
    opti.subject_to(X[:, 0] == x0)

    if model["constraints"]["u_max"] is not None:
        opti.subject_to(U[0, :] <= model["constraints"]["u_max"])
    if model["constraints"]["u_min"] is not None:
        opti.subject_to(U[0, :] >= model["constraints"]["u_min"])

    # State constraints
    for k in range(N):
        opti.subject_to(X[:, k + 1] == F_SSM(X[:, k], U[:, k], V[:, k], dt_data))

    # Objectives
    kM = 1e3
    cost = ca.mtimes(U[0, :], price) + kM * ca.sumsqr(
        ca.fmax(0, X[0, :] - Ti_max) + ca.fmax(0, Ti_min - X[0, :])
    )
    opti.minimize(cost)

    # Solve the optimisation
    sol = solve_optimisation(problem=opti, solver="ipopt", verbose=False)

    # Structuring the outputs
    timeseries = extract_optimisation_results(
        solution=sol, model=model, data=data, X=X, U=U, V=V, keep=["power_price"]
    )

    performance = dict(
        energy_demand=np.sum(timeseries[field_perf_energy]),
        Ti_cold=np.sum(np.fmax(0, timeseries[field_perf_Ti] - Ti_max)),
        Ti_hot=np.sum(np.fmax(0, Ti_min - timeseries[field_perf_Ti])),
    )

    return performance, timeseries
