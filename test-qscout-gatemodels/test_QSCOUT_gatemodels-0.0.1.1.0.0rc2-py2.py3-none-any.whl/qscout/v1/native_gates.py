# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
import numpy as np

from jaqalpaq.core.circuit import normalize_native_gates
from jaqalpaq.core import Parameter, ParamType
from jaqalpaq.core.gatedef import add_idle_gates, GateDefinition, BusyGateDefinition


def U_R(axis_angle, rotation_angle):
    """
    Generates the unitary matrix that describes the QSCOUT native R gate, which performs
    an arbitrary rotation around an axis in the X-Y plane.

    :param float axis_angle: The angle that sets the planar axis to rotate around.
    :param float rotation_angle: The angle by which the gate rotates the state.
    :returns: The unitary gate matrix.
    :rtype: numpy.array
    """
    return np.array(
        [
            [
                np.cos(rotation_angle / 2.0),
                (-1j * np.cos(axis_angle) - np.sin(axis_angle))
                * np.sin(rotation_angle / 2.0),
            ],
            [
                (-1j * np.cos(axis_angle) + np.sin(axis_angle))
                * np.sin(rotation_angle / 2.0),
                np.cos(rotation_angle / 2.0),
            ],
        ]
    )


def U_MS(axis_angle, rotation_angle):
    """
    Generates the unitary matrix that describes the QSCOUT native Mølmer-Sørensen gate.
    This matrix is equivalent to ::

        exp(-i rotation_angle/2 (cos(axis_angle) XI + sin(axis_angle) YI) (cos(axis_angle) IX + sin(axis_angle) IY))

    :param float axis_angle: The phase angle determining the mix of XX and YY rotation.
    :param float rotation_angle: The angle by which the gate rotates the state.
    :returns: The unitary gate matrix.
    :rtype: numpy.array
    """
    return np.array(
        [
            [
                np.cos(rotation_angle / 2.0),
                0,
                0,
                -1j
                * (np.cos(axis_angle * 2.0) - 1j * np.sin(axis_angle * 2.0))
                * np.sin(rotation_angle / 2.0),
            ],
            [0, np.cos(rotation_angle / 2.0), -1j * np.sin(rotation_angle / 2.0), 0],
            [0, -1j * np.sin(rotation_angle / 2.0), np.cos(rotation_angle / 2.0), 0],
            [
                -1j
                * (np.cos(axis_angle * 2.0) + 1j * np.sin(axis_angle * 2.0))
                * np.sin(rotation_angle / 2.0),
                0,
                0,
                np.cos(rotation_angle / 2.0),
            ],
        ]
    )


def U_Rx(rotation_angle):
    return np.array(
        [
            [np.cos(rotation_angle / 2), -1j * np.sin(rotation_angle / 2)],
            [-1j * np.sin(rotation_angle / 2), np.cos(rotation_angle / 2)],
        ]
    )


def U_Ry(rotation_angle):
    return np.array(
        [
            [np.cos(rotation_angle / 2), -np.sin(rotation_angle / 2)],
            [np.sin(rotation_angle / 2), np.cos(rotation_angle / 2)],
        ]
    )


def U_Rz(rotation_angle):
    return np.array([[1, 0], [0, np.exp(1j * rotation_angle)]])


ACTIVE_NATIVE_GATES = (
    BusyGateDefinition("prepare_all"),
    GateDefinition(
        "R",
        [
            Parameter("q", ParamType.QUBIT),
            Parameter("axis-angle", ParamType.FLOAT),
            Parameter("rotation-angle", ParamType.FLOAT),
        ],
        ideal_unitary=U_R,
    ),
    GateDefinition(
        "Rx",
        [Parameter("q", ParamType.QUBIT), Parameter("angle", ParamType.FLOAT)],
        ideal_unitary=U_Rx,
    ),
    GateDefinition(
        "Ry",
        [Parameter("q", ParamType.QUBIT), Parameter("angle", ParamType.FLOAT)],
        ideal_unitary=U_Ry,
    ),
    GateDefinition(
        "Rz",
        [Parameter("q", ParamType.QUBIT), Parameter("angle", ParamType.FLOAT)],
        ideal_unitary=U_Rz,
    ),
    GateDefinition(
        "Px", [Parameter("q", ParamType.QUBIT)], ideal_unitary=lambda: U_Rx(np.pi)
    ),
    GateDefinition(
        "Py", [Parameter("q", ParamType.QUBIT)], ideal_unitary=lambda: U_Ry(np.pi)
    ),
    GateDefinition(
        "Pz", [Parameter("q", ParamType.QUBIT)], ideal_unitary=lambda: U_Rz(np.pi)
    ),
    GateDefinition(
        "Sx", [Parameter("q", ParamType.QUBIT)], ideal_unitary=lambda: U_Rx(np.pi / 2)
    ),
    GateDefinition(
        "Sy", [Parameter("q", ParamType.QUBIT)], ideal_unitary=lambda: U_Ry(np.pi / 2)
    ),
    GateDefinition(
        "Sz", [Parameter("q", ParamType.QUBIT)], ideal_unitary=lambda: U_Rz(np.pi / 2)
    ),
    GateDefinition(
        "Sxd", [Parameter("q", ParamType.QUBIT)], ideal_unitary=lambda: U_Rx(-np.pi / 2)
    ),
    GateDefinition(
        "Syd", [Parameter("q", ParamType.QUBIT)], ideal_unitary=lambda: U_Ry(-np.pi / 2)
    ),
    GateDefinition(
        "Szd", [Parameter("q", ParamType.QUBIT)], ideal_unitary=lambda: U_Rz(-np.pi / 2)
    ),
    GateDefinition(
        "MS",
        [
            Parameter("q0", ParamType.QUBIT),
            Parameter("q1", ParamType.QUBIT),
            Parameter("axis-angle", ParamType.FLOAT),
            Parameter("rotation-angle", ParamType.FLOAT),
        ],
        ideal_unitary=U_MS,
    ),
    GateDefinition(
        "Sxx",
        [Parameter("q0", ParamType.QUBIT), Parameter("q1", ParamType.QUBIT)],
        ideal_unitary=lambda: U_MS(0, np.pi / 2),
    ),
    BusyGateDefinition("measure_all"),
)

ACTIVE_NATIVE_GATES = normalize_native_gates(ACTIVE_NATIVE_GATES)
NATIVE_GATES = add_idle_gates(ACTIVE_NATIVE_GATES)
