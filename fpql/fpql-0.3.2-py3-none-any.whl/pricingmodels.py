import QuantLib as ql
from typing import Optional
from . import ql_enums as qle

def get_qlModel(model: qle.ShortRateModel,
                ts_handle: Optional[ql.QuantLib.YieldTermStructureHandle]=None,
                r0=0.05, 
                a=0.1, 
                b=0.05, 
                sigma=0.01, 
                lamda=0.0,
                eta=0.01, 
                rho=-0.75,
                volstepdates = None, 
                volatilities = None, 
                reversions = None):

    if model == qle.ShortRateModel.vasicek: 
        return ql.Vasicek(r0, a, b, sigma, lamda)
    elif model == qle.ShortRateModel.blackkarasinski:
        return ql.BlackKarasinski(ts_handle, a, sigma)
    elif model == qle.ShortRateModel.hullwhite:
        return ql.HullWhite(ts_handle, a, sigma)
    elif model == qle.ShortRateModel.gsr:
        return ql.Gsr(ts_handle, volstepdates, volatilities, reversions)
    elif model == qle.ShortRateModel.g2:
        return ql.G2(ts_handle, a, sigma, b, eta, rho) 
    else:
        return None




