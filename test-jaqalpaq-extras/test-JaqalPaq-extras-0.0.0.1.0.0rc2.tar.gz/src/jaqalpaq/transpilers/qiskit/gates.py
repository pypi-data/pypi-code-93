# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
# The below classes are a derivative work of Qiskit's Gate class. They have been altered from the original.

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from qiskit.circuit import Gate, QuantumCircuit, QuantumRegister
from qiskit.circuit.library.standard_gates.u3 import U3Gate
from qiskit.circuit.library.standard_gates.rx import RXGate
from qiskit.circuit.library.standard_gates.ry import RYGate
from qiskit.circuit.library.standard_gates.rz import RZGate
from qiskit.circuit.library.standard_gates.rxx import RXXGate
from qiskit.qasm import pi


class JaqalMSGate(Gate):
    """
    The two-parameter Mølmer-Sørensen gate, as implemented on QSCOUT hardware.
    Note that this is *not* equivalent to Qiskit's MSGate. It's equivalent to ::

        exp(-i theta/2 (cos(phi) XI + sin(phi) YI) (cos(phi) IX + sin(phi) IY))

    or to the OpenQASM sequence ::

        gate jaqalms(phi, theta) a,b
        {
        rz(phi) a;
        rz(phi+pi/2) b;
        CX b,a;
        rz(-pi/2) a;
        ry(theta+pi/2) b;
        CX a,b;
        ry(-pi/2) b;
        CX b,a;
        rz(-phi-pi/2) a;
        rz(-phi) b;
        }

    :param float phi: The phase angle determining the mix of XX and YY rotation.
    :param float theta: The angle by which the gate rotates the state.
    :param label: What to label the gate on, e.g., circuit diagrams.
    :type label: str or None
    """

    def __init__(self, phi, theta, label=None):
        super().__init__("jaqalms", 2, [phi, theta], label=label)

    def _define(self):
        """
        gate jaqalms(phi, theta) a,b
        {
        rz(phi) a;
        rz(phi+pi/2) b;
        CX b,a;
        rz(-pi/2) a;
        ry(theta+pi/2) b;
        CX a,b;
        ry(-pi/2) b;
        CX b,a;
        rz(-phi-pi/2) a;
        rz(-phi) b;
        }
        """
        q = QuantumRegister(2, "q")
        qc = QuantumCircuit(q, name=self.name)
        phi, theta = tuple(self.params)
        #         rule = [
        #             (U3Gate(0, 0, phi), [q[0]], []),
        #             (U3Gate(0, 0, phi+pi/2), [q[1]], []),
        #             (CnotGate(), [q[1], q[0]], []),
        #             (U3Gate(0, 0, -pi/2), [q[0]], []),
        #             (U3Gate(theta+pi/2,0,0), [q[1]], []),
        #             (CnotGate(), [q[0], q[1]], []),
        #             (U3Gate(-pi/2,0,0), [q[1]], []),
        #             (CnotGate(), [q[1], q[0]], []),
        #             (U3Gate(0, 0, -phi-pi/2), [q[0]], []),
        #             (U3Gate(0, 0, -phi), [q[1]], []),
        #         ]
        rule = [
            (U3Gate(0, 0, phi), [q[0]], []),
            (U3Gate(0, 0, phi), [q[1]], []),
            (RXXGate(theta), [q[0], q[1]], []),
            (U3Gate(0, 0, -phi), [q[0]], []),
            (U3Gate(0, 0, -phi), [q[1]], []),
        ]
        for inst in rule:
            qc._append(*inst)
        self.definition = qc


def jaqalms(self, phi, theta, a, b):
    return self.append(JaqalMSGate(phi, theta), [a, b], [])


QuantumCircuit.jaqalms = jaqalms


class SYGate(Gate):
    """
    The `sqrt(Y)` gate, as implemented on QSCOUT hardware. It's equivalent to a `pi/2`
    rotation around the Y-axis on the Bloch sphere.

    :param label: What to label the gate on, e.g., circuit diagrams.
    :type label: str or None
    """

    def __init__(self, label=None):
        super().__init__("sy", 1, [], label=label)

    def _define(self):
        """
        gate sy a
        {
        ry(pi/2) a;
        }
        """
        q = QuantumRegister(1, "q")
        qc = QuantumCircuit(q, name=self.name)
        rule = [
            (RYGate(pi / 2), [q[0]], []),
        ]
        for inst in rule:
            qc._append(*inst)
        self.definition = qc


def sy(self, q):
    return self.append(SYGate(), [q], [])


QuantumCircuit.sy = sy


class SYdgGate(Gate):
    """
    The inverse `sqrt(Y)` gate, as implemented on QSCOUT hardware. It's equivalent to a
    `-pi/2` rotation around the Y-axis on the Bloch sphere.

    :param label: What to label the gate on, e.g., circuit diagrams.
    :type label: str or None
    """

    def __init__(self, label=None):
        super().__init__("sydg", 1, [], label=label)

    def _define(self):
        """
        gate sydg a
        {
        ry(-pi/2) a;
        }
        """
        q = QuantumRegister(1, "q")
        qc = QuantumCircuit(q, name=self.name)
        rule = [
            (RYGate(-pi / 2), [q[0]], []),
        ]
        for inst in rule:
            qc._append(*inst)
        self.definition = qc


def sydg(self, q):
    return self.append(SYdgGate(), [q], [])


QuantumCircuit.sydg = sydg


class JaqalRGate(Gate):
    """
    A single-qubit gate representing arbitrary rotation around an axis in the X-Y plane,
    as implemented on QSCOUT hardware. Note that this is essentially a different
    parametrization of Qiskit's U2 gate. It's equivalent to the OpenQASM sequence ::

        gate jaqalr(axis_angle, rotation_angle) a
        {
        rz(-axis_angle) a;
        rx(rotation_angle) a;
        rz(axis_angle) a;
        }

    :param float axis_angle: The angle that sets the planar axis to rotate around.
    :param float rotation_angle: The angle by which the gate rotates the state.
    :param label: What to label the gate on, e.g., circuit diagrams.
    :type label: str or None
    """

    def __init__(self, axis_angle, rotation_angle, label=None):
        super().__init__("jaqalr", 1, [axis_angle, rotation_angle], label=label)

    def _define(self):
        """
        gate jaqalr(axis_angle, rotation_angle) a
        {
        rz(-axis_angle) a;
        rx(rotation_angle) a;
        rz(axis_angle) a;
        }
        """
        q = QuantumRegister(1, "q")
        qc = QuantumCircuit(q, name=self.name)
        axis_angle, rotation_angle = tuple(self.params)
        rule = [
            (RZGate(-axis_angle), [q[0]], []),
            (RXGate(rotation_angle), [q[0]], []),
            (RZGate(axis_angle), [q[0]], []),
        ]
        for inst in rule:
            qc._append(*inst)
        self.definition = qc


def jaqalr(self, axis_angle, rotation_angle, q):
    return self.append(JaqalRGate(axis_angle, rotation_angle), [q], [])


QuantumCircuit.jaqalr = jaqalr
