from dataclasses import dataclass
from typing import List
import mip
from mip import OptimizationStatus
from curvaceous.curve import Curve


@dataclass
class Result:
    status: OptimizationStatus
    xs: List[float]
    ys: List[float]


def maximize(curves: List[Curve], budget: float) -> Result:
    (m, ws) = _create_model(curves, budget)
    status = m.optimize()
    return _to_result(status, curves, ws)


def _create_model(curves: List[Curve], budget: float, print_logs: bool = False):
    m = mip.Model()
    m.solver.set_verbose(1 if print_logs else 0)
    cost = mip.LinExpr()
    value = mip.LinExpr()
    bs = []
    ws = []
    for (i, curve) in enumerate(curves):
        k = len(curve)
        w = [m.add_var(var_type=mip.CONTINUOUS) for _ in range(0, k)]
        b = [m.add_var(var_type=mip.BINARY) for _ in range(0, k - 1)]
        bs.append(b)
        ws.append(w)

        m += mip.xsum(w[i] for i in range(0, k)) == 1
        for i in range(0, k):
            m += w[i] >= 0

        m += w[0] <= b[0]
        for i in range(1, k - 1):
            m += w[i] <= b[i - 1] + b[i]
        m += w[k - 1] <= b[k - 2]
        m += mip.xsum(b[k] for k in range(0, k - 1)) == 1

        for i in range(0, k):
            cost.add_term(w[i] * float(curve.xs[i]))
            value.add_term(w[i] * float(curve.ys[i]))

    m += cost <= budget
    m.objective = mip.maximize(value)
    return (m, ws)


def _to_result(status, curves, ws):
    if status == OptimizationStatus.OPTIMAL:
        return Result(status, *_compute_xs_and_ys(curves, ws))
    return Result(status, None, None)


def _compute_xs_and_ys(curves, ws):
    xs = []
    ys = []
    for (i, curve) in enumerate(curves):
        k = len(curve)
        xs.append(sum(ws[i][j].x * float(curve.xs[j]) for j in range(0, k)))
        ys.append(sum(ws[i][j].x * float(curve.ys[j]) for j in range(0, k)))
    return (xs, ys)
