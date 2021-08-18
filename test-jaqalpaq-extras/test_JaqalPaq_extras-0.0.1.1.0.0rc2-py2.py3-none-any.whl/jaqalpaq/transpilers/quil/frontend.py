# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
from jaqalpaq import JaqalError
import networkx as nx
from pyquil.device import NxDevice
from pyquil.api import QuantumComputer
from pyquil.quilbase import Gate
from pyquil.quilatom import unpack_qubit
from .ioncompiler import IonCompiler
from .qscoutam import QSCOUTAM
import numpy as np
import pyquil


def get_ion_device(num_qubits):
    return NxDevice(nx.complete_graph(num_qubits))


def get_ion_qam():
    return QSCOUTAM()


def get_ion_qc(num_qubits):
    """Constructs a quantum computer object that represents the QSCOUT hardware.
    Unlike the builtin Quil counterparts, it can't run quantum programs, but it can still
    be used as a compilation target and thus used to generate Jaqal code (which can then
    be submitted to be run on the actual QSCOUT device).

    :param int num_qubits: How many qubits in the trap will be used.
    :returns: The quantum computer object for compilation.
    :rtype: pyquil.api.QuantumComputer
    """
    device = get_ion_device(num_qubits)
    return QuantumComputer(
        name="QSCOUT-%d" % num_qubits,
        qam=get_ion_qam(),
        device=device,
        compiler=IonCompiler(device),
    )


def quil_gates(native_gates=None):
    """Generates quil versions of a gate set (the QSCOUT native gates, by default).

    :returns: A mapping of gate names to functions that take classical parameters and
        qubit indices and build pyquil gates.
    :rtype: dict

    .. warning::
        PyQuil simulators will give an error if QSCOUT native gates are passed to them!
    """
    dkt = {}
    if native_gates is None:
        from qscout.v1.std import NATIVE_GATES

        native_gates = NATIVE_GATES

    gates = {}

    for gate in native_gates:
        if native_gates[gate].ideal_unitary is None:
            continue
        quil_name = gate.upper()
        classical_count = len(native_gates[gate].classical_parameters)
        if classical_count != 0:
            gates[quil_name] = (
                lambda quil_name, classical_count: (
                    lambda *args: Gate(
                        name=quil_name,
                        params=args[:classical_count],
                        qubits=[unpack_qubit(q) for q in args[classical_count:]],
                    )
                )
            )(quil_name, classical_count)
        else:
            gates[quil_name] = (
                lambda quil_name: (
                    lambda *args: Gate(
                        name=quil_name,
                        params=[],
                        qubits=[unpack_qubit(q) for q in args],
                    )
                )
            )(quil_name)
    return gates
