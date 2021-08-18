# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
from pytket.circuit import OpType

from jaqalpaq.core.circuitbuilder import (
    CircuitBuilder,
    UnscheduledBlockBuilder,
    SequentialBlockBuilder,
)

import numpy as np

from jaqalpaq import JaqalError

_TKET_NAMES = {
    OpType.PhasedX: lambda q, alpha, beta: ("R", q, beta, alpha),
    OpType.Rz: lambda q, theta: ("Rz", q, theta),
    OpType.XXPhase: lambda q1, q2, theta: ("MS", q1, q2, 0, theta),
}


def jaqal_circuit_from_tket_circuit(
    tkc, native_gates=None, names=None, remove_measurements=False
):
    """Converts a pytket Circuit object to a :class:`jaqalpaq.core.Circuit`.
    The circuit will be structured as a sequence of parallel blocks, one for each Cirq
    Moment in the input. The circuit will be structured into a sequence of unscheduled
    blocks. All instructions between one barrier statement and the next will be put into
    an unscheduled block together. If the :mod:`jaqalpaq.scheduler` is run on the circuit,
    as many as possible of those gates will be parallelized within each block, while
    maintaining the order of the blocks. Otherwise, the circuit will be treated as a fully
    sequential circuit.

    Measurement commands are supported, but only if applied to every qubit in the circuit
    in immediate succession. If so, they will be mapped to a measure_all gate. If the
    circuit does not end with a measurement, then a measure_all gate will be appended to
    it.

    Circuits containing multiple quantum registers will be converted to circuits with a
    single quantum register, containing all the qubits from each register. The parts of
    that larger register that correspond to each of the original registers will be mapped
    with the appropriate names. Circuits containing multiple-index qubits will have each
    such qubit mapped to a single-qubit register named with the indices separated by
    underscore characters.

    Measurements are supported, but only if applied to every qubit in the circuit in the
    same moment. If so, they will be mapped to a measure_all gate. If the measure_all gate
    is not the last gate in the circuit, a prepare_all gate will be inserted after it.
    Additionally, a prepare_all gate will be inserted before the first moment. If the
    circuit does not end with a measurement, then a measure_all gate will be appended.

    :param pytket.circuit.Circuit tkc: The Circuit to convert.
    :param names: A mapping from pytket OpTypes to functions taking qubits and gate
    angle parameters and returning a tuple of arguments for
        :meth:`jaqalpaq.core.Circuit.build_gate`. If omitted, maps
        ``pytket.OpType.PhasedX`` to the QSCOUT ``R`` gate, ``pytket.OpType.Rz`` to the
        QSCOUT ``Rz`` gate, and ``pytket.OpType.XXPhase`` to the QSCOUT ``MS`` gate. The
        ``pytket.passes.SynthesizeUMD`` compilation pass will compile a circuit into this
        basis.
    :type names: dict or None
    :param native_gates: The native gate set to target. If None, target the QSCOUT native
        gates.
    :type native_gates: dict or None
    :param bool remove_measurements: Ignore any measure statements in the original circuit
        and append a measure_all gate instead. Defaults to False.
    :returns: The same quantum circuit, converted to JaqalPaq.
    :rtype: jaqalpaq.core.Circuit
    :raises JaqalError: If the circuit includes a gate not included in `names`.
    """
    qreg_sizes = {}
    for qb in tkc.qubits:
        if len(qb.index) != 1:
            qreg_sizes[qb.reg_name + "_".join([str(x) for x in qb.index])] = 1
        elif qb.reg_name in qreg_sizes:
            qreg_sizes[qb.reg_name] = max(qreg_sizes[qb.reg_name], qb.index[0] + 1)
        else:
            qreg_sizes[qb.reg_name] = qb.index[0] + 1
    n = sum(qreg_sizes.values())
    if native_gates is None:
        from qscout.v1.std import NATIVE_GATES

        native_gates = NATIVE_GATES
    qsc = CircuitBuilder(native_gates=native_gates)
    if names is None:
        names = _TKET_NAMES
    baseregister = qsc.register("baseregister", n)
    offset = 0
    registers = {}
    for qreg in qreg_sizes:
        registers[qreg] = qsc.map(
            qreg, baseregister, slice(offset, offset + qreg_sizes[qreg])
        )
        offset += qreg_sizes[qreg]
    # We're going to divide the circuit up into blocks. Each block will contain every gate
    # between one barrier statement and the next. If the circuit is output with no further
    # processing, then the gates in each block will be run in sequence. However, if the
    # circuit is passed to the scheduler, it'll try to parallelize as many of the gates
    # within each block as possible, while keeping the blocks themselves sequential.
    block = UnscheduledBlockBuilder()
    qsc.expression.append(block.expression)
    block.gate("prepare_all")
    measure_accumulator = set()
    for command in tkc:
        block, measure_accumulator = convert_command(
            command,
            qsc,
            block,
            names,
            measure_accumulator,
            n,
            registers,
            remove_measurements,
        )
    block.gate("measure_all", no_duplicate=True)
    return qsc.build()


def convert_command(
    command,
    qsc,
    block,
    names,
    measure_accumulator,
    n,
    registers,
    remove_measurements,
    remaps=None,
):
    if remaps is None:
        remaps = range(n)
    op_type = command.op.type
    if measure_accumulator:
        if op_type == OpType.Measure:
            qb = command.qubits[0]
            if qb.reg_name in registers:
                if len(qb.index) != 1:
                    target = registers[
                        qb.reg_name + "_".join([str(x) for x in qb.index])
                    ][0]
                else:
                    target = registers[qb.reg_name][qb.index[0]]
                measure_accumulator.add(target.resolve_qubit()[1])
            else:
                raise JaqalError("Register %s invalid!" % target.register.name)
            if len(measure_accumulator) == n:
                block.gate("measure_all")
                measure_accumulator = set()
            return block, measure_accumulator
        else:
            raise JaqalError(
                "Cannot measure only qubits %s and not whole register."
                % measure_accumulator
            )
            # measure_accumulator = set()
    if op_type == OpType.Measure:
        if not remove_measurements:
            qb = command.qubits[0]
            if len(qb.index) != 1:
                target = registers[qb.reg_name + "_".join([str(x) for x in qb.index])][
                    0
                ]
            else:
                target = registers[qb.reg_name][qb.index[0]]
            measure_accumulator = {target.resolve_qubit()[1]}
            if len(measure_accumulator) == n:
                block.gate("measure_all")
                measure_accumulator = set()
    elif op_type == OpType.Barrier:
        block = UnscheduledBlockBuilder()
        qsc.expression.append(block.expression)
        # Use barriers to inform the scheduler, as explained above.
    elif op_type in (OpType.CircBox, OpType.ExpBox, OpType.PauliExpBox):
        new_remaps = [remaps[qb.index[0]] for qb in command.qubits]
        macro_block = SequentialBlockBuilder()
        subcirq = command.op.get_circuit()
        for cmd in subcirq:
            convert_command(
                cmd,
                qsc,
                macro_block,
                names,
                set(),
                n,
                registers,
                remove_measurements,
                new_remaps,
            )
        macro_name = f"macro_{len(qsc.macros)}"
        qsc.macro(macro_name, [], macro_block)
        block.append(qsc.build_gate(macro_name))
        # TODO: Re-use macros when the same circuit block appears in multiple places.
    elif op_type in names:
        targets = command.qubits
        qb_targets = []
        for qb in targets:
            if (
                len(qb.index) != 1
            ):  # TODO: Figure out how to pass multi-index qubits in macros.
                qb_targets.append(
                    registers[qb.reg_name + "_".join([str(x) for x in qb.index])][0]
                )
            else:
                qb_targets.append(registers[qb.reg_name][remaps[qb.index[0]]])
        block.gate(
            *names[op_type](
                *qb_targets,
                *[float(param) * np.pi for param in command.op.params],
            )
        )
    else:
        raise JaqalError(
            "Instruction %s not available on trapped ion hardware; try unrolling first."
            % op_type
        )
    return block, measure_accumulator
