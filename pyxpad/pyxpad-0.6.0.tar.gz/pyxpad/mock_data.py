from collections import defaultdict
from typing import Union
import numpy as np
from pyxpad.pyxpad_utils import XPadDataDim, XPadDataItem


class MockSignalData:
    pass


MOCK_SIGNALS = [
    ["signal_a", ""],
    ["signal_b", "This one has something"],
    ["signal_c", ""],
    ["first_signal", ""],
    ["second_signal", "a description"],
]

MOCK_DEFAULT_SHOT = [MOCK_SIGNALS[0], MOCK_SIGNALS[1], MOCK_SIGNALS[2], MOCK_SIGNALS[4]]

MOCK_LAST_SHOT = "12354"

MOCK_SHOTS = defaultdict(
    lambda: MOCK_DEFAULT_SHOT,
    (
        (MOCK_LAST_SHOT, [MOCK_SIGNALS[1], MOCK_SIGNALS[2], MOCK_SIGNALS[3]]),
        ("45321", [MOCK_SIGNALS[0], MOCK_SIGNALS[1], MOCK_SIGNALS[4]]),
        ("1", MOCK_SIGNALS),
    ),
)


class MockClient:
    """Mock UDA Client"""

    @staticmethod
    def get(name: str, shot: Union[int, str]):
        if name == "lastshot":
            child = MockSignalData()
            child.lastshot = int(MOCK_LAST_SHOT)
            signal = MockSignalData()
            signal.children = [child]
            return signal
        if name.startswith("meta::list"):
            signal = MockSignalData()
            shot_data = MOCK_SHOTS[str(shot).strip()]
            signal.signal_name = [item[0] for item in shot_data]
            signal.description = [item[1] for item in shot_data]
            return {"data": signal}
        x = np.linspace(0.0, 1.0)
        dim = XPadDataDim({"name": "time", "data": x})
        data = XPadDataItem({"name": name, "data": np.sin(x), "dim": [dim]})
        return data
