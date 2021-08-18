# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
from jaqalpaq.core import CircuitBuilder
from jaqalpaq import JaqalError

import numpy as np


def _CIRQ_NAMES():
    """(cached) Mapping of Cirq gates to Jaqal-compatible functions."""
    global _CIRQ_NAMES_cache
    try:
        return _CIRQ_NAMES_cache
    except NameError:
        pass

    from cirq import (
        XXPowGate,
        XPowGate,
        YPowGate,
        ZPowGate,
        PhasedXPowGate,
    )

    _CIRQ_NAMES_cache = {
        XXPowGate: (lambda g, q1, q2: ("MS", q1, q2, 0, g.exponent * np.pi)),
        XPowGate: (lambda g, q: ("R", q, 0, g.exponent * np.pi)),
        YPowGate: (lambda g, q: ("R", q, 90.0, g.exponent * np.pi)),
        ZPowGate: (lambda g, q: ("Rz", q, g.exponent * np.pi)),
        PhasedXPowGate: (
            lambda g, q: ("R", q, g.phase_exponent * np.pi, g.exponent * np.pi)
        ),
    }
    return _CIRQ_NAMES_cache


def jaqal_circuit_from_cirq_circuit(ccirc, names=None, native_gates=None):
    """Converts a Cirq Circuit object to a :class:`jaqalpaq.core.Circuit`.
    The circuit will be structured as a sequence of parallel blocks, one for each Cirq
    Moment in the input.

    Measurement are supported, but only if applied to every qubit in the circuit in the
    same moment. If so, they will be mapped to a measure_all gate. If the measure_all gate
    is not the last gate in the circuit, a prepare_all gate will be inserted after it.
    Additionally, a prepare_all gate will be inserted before the first moment. If the
    circuit does not end with a measurement, then a measure_all gate will be appended.

    Circuits built on a line register will map each qubit to the qubit of the same index
    on the hardware. This may leave some qubits unused. Otherwise, the qubits will be
    mapped onto the hardware in the order given by ccirc.all_qubits().

    :param cirq.Circuit ccirc: The Circuit to convert.
    :param names: A mapping from Cirq gate classes to the corresponding native Jaqal gate
        names. If omitted, maps ``cirq.XXPowGate``, ``cirq.XPowGate``, ``cirq.YPowGate``,
        ``cirq.ZPowGate``, and ``cirq.PhasedXPowGate`` to their QSCOUT counterparts. The
        ``cirq.ConvertToIonGates`` function will transpile a circuit into this basis.
    :type names: dict or None
    :param native_gates: The native gate set to target. If None, target the QSCOUT native gates.
    :type native_gates: dict or None
    :returns: The same quantum circuit, converted to JaqalPaq.
    :rtype: Circuit
    :raises JaqalError: If the circuit includes a gate not included in `names`.
    """
    from cirq import MeasurementGate

    if native_gates is None:
        from qscout.v1.std import NATIVE_GATES

        native_gates = NATIVE_GATES
    builder = CircuitBuilder(native_gates=native_gates)
    if names is None:
        names = _CIRQ_NAMES()
    try:
        n = 1 + max([qb.x for qb in ccirc.all_qubits()])
        line = True
    except:
        cqubits = ccirc.all_qubits()
        n = len(cqubits)
        qubitmap = {cqubits[i]: i for i in range(n)}
        line = False
    allqubits = builder.register("allqubits", n)
    need_prep = True
    for moment in ccirc:
        if len(moment) == 0:
            continue
        if need_prep:
            builder.gate("prepare_all")
            need_prep = False
        if (
            len(moment) == n
            and all([op.gate for op in moment])
            and all([isinstance(op.gate, MeasurementGate) for op in moment])
        ):
            builder.gate("measure_all")
            need_prep = True
            continue
        if len(moment) > 1:
            block = builder.block(parallel=True)
            # Note: If you tell Cirq you want MS gates in parallel, we'll generate a Jaqal
            # file with exactly that, never mind that QSCOUT can't execute it.
        else:
            block = builder
        for op in moment:
            if op.gate:
                gate_type = None
                for name in names:
                    if isinstance(op.gate, name):
                        gate_type = name
                        break
                if gate_type:
                    if line:
                        targets = [allqubits[qb.x] for qb in op.qubits]
                    else:
                        targets = [allqubits[qubitmap[qb]] for qb in op.qubits]
                    block.gate(*names[gate_type](op.gate, *targets))
                else:
                    raise JaqalError(
                        "Convert %s to ion gates before compiling." % str(type(op.gate))
                    )
            else:
                raise JaqalError("Cannot compile operation %s." % op)
    if not need_prep:
        # If we just measured, or the circuit is empty, don't add a final measurement.
        builder.gate("measure_all")
    return builder.build()
