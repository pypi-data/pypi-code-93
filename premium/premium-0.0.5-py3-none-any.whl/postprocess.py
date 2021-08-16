#!/usr/bin/env python
import codefast as cf
import numpy as np
import pandas as pd


class Mop:
    def blend(self,
              files: str,
              columns: list,
              to: str = '/tmp/blender.csv') -> bool:
        assert all(cf.io.exists(f) for f in files)
        dfs = [pd.read_csv(f) for f in files]
        target = dfs[0]
        for c in columns:
            cf.info(c)
            for _df in dfs[1:]:
                target[c] += _df[c]
            target[c] /= len(dfs)
        target.to_csv(to, index=False)


mop = Mop()


def get_binary_prediction(y_pred: list, threshold: float = 0.5):
    cf.info(f'Get binary prediction of y_pred')
    ans = []
    for e in y_pred:
        if isinstance(e, int) or isinstance(e, float):
            assert 0 <= e <= 1
            ans.append(1 if e >= threshold else 0)
        elif isinstance(e, list) or isinstance(e, np.ndarray):
            assert len(e) == 1, 'item should contains only one number.'
            n_float = float(e[0])
            assert 0 <= n_float <= 1
            ans.append(1 if n_float >= threshold else 0)
        else:
            print(e, type(e))
            raise TypeError('Unsupported element type.')
    return ans
