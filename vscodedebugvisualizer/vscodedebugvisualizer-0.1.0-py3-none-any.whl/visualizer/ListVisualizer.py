import json

import numpy as np
from vscodedebugvisualizer.visualizer.NumpyVisualizer import NumpyVisualizer


class ListVisualizer:
    def checkType(self, t):
        return isinstance(t, list)

    def getCols(self, l):
        columns = []
        for c in l:
            columns.append({"content": c})

        return columns

    def getRow(self, l):
        return {"columns": self.getCols(l)}

    def visualize(self, l: list):
        npList = np.array(l)
        if npList.dtype.type is not np.str_:
            return NumpyVisualizer().visualize(npList)

        rows = []
        if len(npList.shape) == 1:
            rows.append(self.getRow(npList))
        else:
            for r in npList:
                rows.append(self.getRow(npList))

        d = {
            "kind": {"grid": True},
            "text": "test",
            "rows": rows,
        }

        return json.dumps(d)
