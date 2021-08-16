# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
from jaqalpaq.core import (
    BlockStatement,
    LoopStatement,
    GateStatement,
    ParamType,
    Circuit,
)
from jaqalpaq.core.block import UnscheduledBlockStatement
from jaqalpaq.core.algorithm.visitor import Visitor
from jaqalpaq.core.algorithm.used_qubit_visitor import UsedQubitIndicesVisitor
from jaqalpaq import JaqalError


def schedule_circuit(circ):
    """
    Takes every :class:`jaqalpaq.core.BlockStatement` that has been flagged unscheduled,
    and replaces it with a block that is functionally identical (contains the same gates,
    without reordering any non-commuting operations); complies with the restrictions of
    the QSCOUT hardware and low-level software stack; and reorders gates to act in
    parallel where possible.

    Currently the restrictions on parallelization are:

    * Two-qubit gates cannot occur in parallel with any other operation.
    * State preparation and measurement cannot occur in parallel with any other operation.
    * No qubit can be involved in multiple simultaneous gates.
    * Macro-defined gates cannot occur in parallel with any other operation.
    * Loop statements cannot occur in parallel with any other operation.

    These restrictions are not enforced by Jaqal itself, and other submodules may generate
    code that does not comply with them if instructed to by the user, but they will not
    execute on the current version of the QSCOUT hardware, and so this scheduler does not
    introduce them.

    Additionally, sequential blocks cannot be nested directly in other sequential blocks;
    when the process of scheduling creates such a nesting, it will automatically replace
    the inner block with every gate it contains.

    :param Circuit circ: The circuit to parallelize.
    :returns: The rescheduled circuit. This may share some data with the original circuit,
        which should not be modified.
    """

    visitor = SchedulerVisitor()
    return visitor.visit(circ)


class SchedulerVisitor(Visitor):
    def visit_default(self, obj):
        return obj

    def visit_Circuit(self, circ):
        self.all_qubits = {}
        for reg in circ.fundamental_registers():
            self.all_qubits[reg.name] = set(range(reg.size))

        self.native_gates = circ.native_gates
        self.body = circ.body
        new_circuit = Circuit(native_gates=circ.native_gates)
        new_circuit.constants.update(circ.constants)
        new_circuit.registers.update(circ.registers)
        new_circuit.macros.update(circ.macros)
        new_circuit.body.statements.extend(self.visit(circ.body).statements)
        return new_circuit

    def visit_BlockStatement(self, block):
        new_statements = []
        if isinstance(block, UnscheduledBlockStatement):
            used_qubits = _get_used_qubit_indices(block, self.all_qubits)
            freeze_timestamps = {
                regname: {idx: -1 for idx in used_qubits[regname]}
                for regname in used_qubits
            }
            for instr in block:
                self.schedule_instr(instr, new_statements, freeze_timestamps)
            for moment in range(len(new_statements)):
                if isinstance(new_statements[moment], list):
                    if len(new_statements[moment]) > 1:
                        new_statements[moment] = BlockStatement(
                            statements=new_statements[moment], parallel=True
                        )
                    else:
                        new_statements[moment] = new_statements[moment][0]
        elif block.parallel:
            for instr in block:
                if isinstance(instr, BlockStatement) or isinstance(
                    instr, LoopStatement
                ):
                    new_statements.append(self.visit(instr))
                else:
                    new_statements.append(instr)
        else:
            for instr in block:
                if isinstance(instr, BlockStatement):
                    if instr.parallel or block is self.body:
                        new_statements.append(self.visit(instr))
                    else:
                        new_statements.extend(self.visit(instr).statements)
                elif isinstance(instr, LoopStatement):
                    new_statements.append(self.visit(instr))
                else:
                    new_statements.append(instr)
        return BlockStatement(statements=new_statements, parallel=block.parallel)

    def visit_LoopStatement(self, loop):
        return LoopStatement(loop.iterations, self.visit(loop.statements))

    def schedule_instr(self, instr, target, freeze_timestamps, after=-1):
        used_qubits = _get_used_qubit_indices(instr, self.all_qubits)
        is_block = isinstance(instr, BlockStatement)
        is_gate = isinstance(instr, GateStatement)
        is_loop = isinstance(instr, LoopStatement)
        if (is_block and instr.parallel) or is_gate:
            defrost = 0
            for reg in used_qubits:
                for idx in used_qubits[reg]:
                    defrost = max(after + 1, defrost, freeze_timestamps[reg][idx] + 1)
            while defrost < len(target) and not self.can_parallelize(
                target[defrost], instr, used_qubits
            ):
                defrost += 1
            if defrost >= len(target):
                target.append([instr])
            elif is_block:
                target[defrost].extend(instr.statements)
            else:
                target[defrost].append(instr)
        elif is_block:
            # You can't nest two sequential blocks, so we flatten the block.
            for sub_instr in instr:
                after = self.schedule_instr(sub_instr, target, freeze_timestamps, after)
            return after  # We've frozen all the relevant qubits already.
        elif is_loop:
            # Loop statements can't be parallelized with anything; just stick it at the end
            defrost = len(target)  # Any qubit used in the loop shouldn't be touched
            target.append([instr])  # Until after the loop finishes
        else:
            raise JaqalError("Can't schedule instruction %s." % str(instr))
        for reg in used_qubits:
            for idx in used_qubits[reg]:
                freeze_timestamps[reg][idx] = defrost
        return defrost

    def can_parallelize(self, moment, instr, qubits):
        for other_instr in moment:
            other_used_qubits = _get_used_qubit_indices(other_instr, self.all_qubits)
            for reg in other_used_qubits:
                if reg in qubits and not other_used_qubits[reg].isdisjoint(qubits[reg]):
                    return False  # Can't act on the same qubit twice simultaneously.

            if not self.can_parallelize_subinstr(other_instr):
                return False

            if isinstance(instr, BlockStatement):
                for sub_instr in instr:
                    if not self.can_parallelize_gate(moment, sub_instr, qubits):
                        return False  # If we can parallelize all the components, we can parallelize the block.
            elif isinstance(instr, GateStatement):
                return self.can_parallelize_gate(moment, instr, qubits)
            else:
                return False  # We don't know what this is, so we can't parallelize it.
        return True

    def can_parallelize_gate(self, block, instr, qubits):
        if not self.can_parallelize_subinstr(instr):
            return False
        else:
            # We could do other checks here, but right now there's nothing we need to worry
            # about. Specifically, if there were two instructions that couldn't be in parallel
            # with each other, even on different qubits, but could be in parallel with other
            # instructions, this is where we'd test for it. I expect this and
            # can_parallelize_subinstr to change as our hardware evolves, whereas everything
            # above shouldn't need to, since it tests for limitations like qubit overlap that
            # aren't dependent on a specific hardware implementation.
            return True

    def can_parallelize_subinstr(self, sub_instr):
        if not isinstance(sub_instr, GateStatement):
            return False  # Too much nested structure.
        if sub_instr.name not in self.native_gates:
            return False  # Can't do macros in parallel, because they could include anything.
        if len(self.native_gates[sub_instr.name].quantum_parameters) > 1:
            return False  # Can't do multiple 2-qubit gates at once.
        return True


def _get_used_qubit_indices(obj, all_qubits=None):
    visitor = UsedQubitIndicesVisitor()
    visitor.all_qubits = all_qubits
    return visitor.visit(obj)
