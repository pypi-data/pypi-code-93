# Copyright 2019-2021 Cambridge Quantum Computing
#
# You may not use this file except in compliance with the Licence.
# You may obtain a copy of the Licence in the LICENCE file accompanying
# these documents or at:
#
#     https://cqcl.github.io/pytket/build/html/licence.html
"""Parser from OPENQASM to tket Circuits"""

__path__ = __import__("pkgutil").extend_path(__path__, __name__)  # type: ignore

from .qasm import (
    circuit_from_qasm,
    circuit_to_qasm,
    circuit_from_qasm_str,
    circuit_to_qasm_str,
    circuit_from_qasm_io,
    circuit_to_qasm_io,
)
