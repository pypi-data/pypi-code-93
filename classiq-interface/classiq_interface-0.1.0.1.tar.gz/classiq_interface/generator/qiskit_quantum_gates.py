import enum


class QiskitBuiltinQuantumGates(str, enum.Enum):
    # TODO: Not using 'I' due to https://www.flake8rules.com/rules/E741.html
    I = "I"
    X = "X"
    Y = "Y"
    Z = "Z"
    T = "T"
    S = "S"
    H = "H"
    P = "P"
    CX = "CX"
    CY = "CY"
    CZ = "CZ"
    CCX = "CCX"
    RY = "RY"
    CRY = "CRY"
