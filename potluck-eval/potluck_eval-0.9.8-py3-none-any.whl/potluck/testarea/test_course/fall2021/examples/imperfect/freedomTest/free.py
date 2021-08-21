"""
Freedom test task imperfect example.

free.py

Peter Mawhorter 2021-7-23
"""


def whatever(a, b):
    """
    Incorrect implementation that returns different values in three
    circumstances and crashes in the fourth.
    """
    if a and b:
        return "Both"
    elif a and not b: # incorrect logic
        return "A"
    elif b:
        return "B"
    else:
        raise ValueError("Crash!")


# Expectations

import optimism as opt


# Not enough expectations (3 required)
opt.testCase(whatever(True, True))
opt.expectResult("Both")
# Expectation fails (without crashing):
opt.testCase(whatever(True, False))
opt.expectResult("B")
