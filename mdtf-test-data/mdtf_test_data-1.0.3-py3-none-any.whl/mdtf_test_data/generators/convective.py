import numpy as np


def convective(xyshape, ntimes, varname="missing"):

    np.random.seed(ntimes)

    valid_varnames = ["tave", "qsat_int", "cwv", "pr"]
    assert (
        varname in valid_varnames
    ), f"Variable '{varname}' is not valid for the convective generator"

    nlat = xyshape[0]
    nlon = xyshape[1]
    arrshape = (ntimes, nlat, nlon)

    results = {}

    # units=K
    results["tave"] = np.random.binomial(10, 0.5, size=arrshape) + 265.0

    # units=mm
    if varname in ["qsat_int", "cwv", "pr"]:
        results["qsat_int"] = 57.0 + (results["tave"] - 268.0) * (82.0 - 57.0) / (
            274.0 - 268.0
        )

    # units=mm
    if varname in ["cwv", "pr"]:
        cwv = results["qsat_int"] - 2.0 * np.random.chisquare(4, size=arrshape)
        cwv[cwv <= 0.0] = results["qsat_int"][cwv <= 0.0]
        results["cwv"] = cwv

    # units=m/s
    if varname == "pr":
        w_minus_wc = results["cwv"] - (
            50.0 + (results["tave"] - 268.0) * (67.0 - 50.0) / (274.0 - 268.0)
        )  # Units: mm
        pr = (1.0 / 3.6e6) * (
            np.log(1 + np.exp(0.6 * (w_minus_wc)))
            + 0.2 * np.random.normal(0.0, 0.5, size=arrshape)
        )
        results["pr"] = pr

    return results[varname]
