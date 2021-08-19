# Copyright 2019-2021 Cambridge Quantum Computing
#
# You may not use this file except in compliance with the Licence.
# You may obtain a copy of the Licence in the LICENCE file accompanying
# these documents or at:
#
#     https://cqcl.github.io/pytket/build/html/licence.html
"""Utility functions for performing high-level procedures in pytket"""

from .expectations import (
    expectation_from_shots,
    expectation_from_counts,
    get_pauli_expectation_value,
    get_operator_expectation_value,
)
from .measurements import append_pauli_measurement
from .prepare import prepare_circuit
from .results import (
    counts_from_shot_table,
    probs_from_counts,
    probs_from_state,
    permute_qubits_in_statevector,
    permute_basis_indexing,
    permute_rows_cols_in_unitary,
    compare_statevectors,
    compare_unitaries,
)
from .term_sequence import gen_term_sequence_circuit
from .operators import QubitPauliOperator
from .outcomearray import OutcomeArray, readout_counts
from .graph import Graph
from .symbolic import circuit_to_symbolic_unitary, circuit_apply_symbolic_statevector
