import numpy as np
import psycopg2


def nan_to_null(
    f, _NULL=psycopg2.extensions.AsIs("NULL"), _NaN=np.NaN, _Float=psycopg2.extensions.Float,
):
    psycopg2.extensions.register_adapter(float, nan_to_null)
    if not np.isnan(f):
        return _Float(f)
    return _NULL
