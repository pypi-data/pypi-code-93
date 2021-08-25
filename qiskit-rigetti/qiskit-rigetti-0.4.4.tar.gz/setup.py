# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qiskit_rigetti', 'qiskit_rigetti.gates', 'qiskit_rigetti.hooks']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.20.1,<2.0.0', 'pyquil>=3.0.0,<4.0.0', 'qiskit>=0.27.0,<0.28.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata'],
 'docs': ['sphinx>=4.1.1,<5.0.0',
          'sphinx-autoapi>=1.8.1,<2.0.0',
          'furo>=2021.7.5-beta.38,<2022.0.0',
          'myst-parser>=0.15.1,<0.16.0',
          'sphinx-autobuild>=2021.3.14,<2022.0.0',
          'nbsphinx>=0.8.6,<0.9.0',
          'ipython>=7.25.0,<8.0.0']}

setup_kwargs = {
    'name': 'qiskit-rigetti',
    'version': '0.4.4',
    'description': 'Provider for running Qiskit circuits on Rigetti QPUs and simulators.',
    'long_description': '[![Tests](https://github.com/rigetti/qiskit-rigetti/actions/workflows/test.yml/badge.svg)](https://github.com/rigetti/qiskit-rigetti/actions/workflows/test.yml)\n[![Documentation Status](https://readthedocs.org/projects/qiskit-rigetti/badge/?version=latest)](https://qiskit-rigetti.readthedocs.io/en/latest/?badge=latest)\n[![pypi](https://img.shields.io/pypi/v/qiskit-rigetti.svg)](https://pypi.org/project/qiskit-rigetti/)\n[![Binder](https://mybinder.org/badge_logo.svg)][binder]\n\n# Rigetti Provider for Qiskit\n\n## Try It Out\n\nTo try out this library, you can run example notebooks in a pre-made [binder][binder]. Alternately, you can run the following to build and run the image locally:\n\n```bash\ndocker build -t qiskit-tutorials .\ndocker run --rm -p 8888:8888 qiskit-tutorials\n```\n\nthen click on the link that is displayed after the container starts up.\n\n[binder]: https://mybinder.org/v2/gh/rigetti/qiskit-rigetti/main?filepath=examples\n\n## Pre-requisites\n\n1. Install [Docker](https://www.docker.com/products/docker-desktop)\n1. Download [qelib1.inc](https://raw.githubusercontent.com/Qiskit/qiskit-terra/0.16.2/qiskit/qasm/libs/qelib1.inc)\n1. Place `qelib1.inc` in a folder called `inc` in the project root\n\n## Setup QVM and quilc\n\n### Using Docker Compose\n\nRun `docker compose up` to see service logs or `docker compose up -d` to run in the background.\n\n### Using Docker Manually\n\n1. Start the QVM:\n   \n   ```bash\n   docker run --rm -it -p 5000:5000 rigetti/qvm -S\n   ```\n\n1. Start the compiler:\n\n   ```bash\n   docker run --rm -it -p 5555:5555 -v "$PWD"/inc:/inc rigetti/quilc -S -P --safe-include-directory /inc/\n   ```\n\n## Usage\n\nExample:\n\n```python\nfrom qiskit import execute\nfrom qiskit_rigetti import RigettiQCSProvider, QuilCircuit\n\n# Get provider and backend\np = RigettiQCSProvider()\nbackend = p.get_simulator(num_qubits=2, noisy=True)  # or p.get_backend(name=\'Aspen-9\')\n\n# Create a Bell state circuit\ncircuit = QuilCircuit(2, 2)\ncircuit.h(0)\ncircuit.cx(0, 1)\ncircuit.measure([0, 1], [0, 1])\n\n# Execute the circuit on the backend\njob = execute(circuit, backend, shots=10)\n\n# Grab results from the job\nresult = job.result()\n\n# Return memory and counts\nmemory = result.get_memory(circuit)\ncounts = result.get_counts(circuit)\nprint("Result memory:", memory)\nprint("Result counts:", counts)\n```\n\n### Rigetti Quantum Cloud Services (QCS)\n\nExecution against a QPU requires a [reservation via QCS](https://docs.rigetti.com/qcs/guides/reserving-time-on-a-qpu).\nFor more information on using QCS, see the [QCS documentation](https://docs.rigetti.com).\n\n## Advanced\n\n### Lifecycle Hooks\n\nFor advanced QASM and Quil manipulation, `before_compile` and `before_execute` keyword arguments can be passed to\n`RigettiQCSBackend.run()` or to Qiskit\'s `execute()`.\n\n#### Pre-compilation Hooks\n\nAny `before_compile` hooks will apply, in order, just before compilation from QASM to native Quil.\nFor example:\n\n```python\n...\n\ndef custom_hook_1(qasm: str) -> str:\n   new_qasm = ...\n   return new_qasm\n\ndef custom_hook_2(qasm: str) -> str:\n   new_qasm = ...\n   return new_qasm\n\njob = execute(circuit, backend, shots=10, before_compile=[custom_hook_1, custom_hook_2])\n\n...\n```\n\n#### Pre-execution Hooks\n\nAny `before_execute` hooks will apply, in order, just before execution (after translation from QASM to native Quil).\nFor example:\n\n```python\nfrom pyquil import Program\n\n...\n\ndef custom_hook_1(quil: Program) -> Program:\n   new_quil = ...\n   return new_quil\n\ndef custom_hook_2(quil: Program) -> Program:\n   new_quil = ...\n   return new_quil\n\njob = execute(circuit, backend, shots=10, before_execute=[custom_hook_1, custom_hook_2])\n\n...\n```\n\n> **Note**:\n> \n> Only [certain forms of Quil can can be executed on a QPU](https://pyquil-docs.rigetti.com/en/stable/compiler.html?highlight=protoquil#legal-compiler-input).\n> If pre-execution transformations produce a final program that is not QPU-compliant, `ensure_native_quil=True` can be\n> passed to `execute()` or `RigettiQCSBackend.run()` to recompile the final Quil program to native Quil prior to\n> execution. If no pre-execution hooks were supplied, this setting is ignored. If this setting is omitted, a value of\n> `False` is assumed.\n> \n> _Example_: Adding the Quil instruction `H 0` would result in an error if `ensure_native_quil=False` and the QPU does\n> not natively implement Hadamard gates.\n\n#### Built-in Hooks\n\nThe `hooks.pre_compilation` and `hooks.pre_execution` packages provide a number of convenient hooks:\n\n##### `set_rewiring`\n\nUse `set_rewiring` to provide a [rewiring directive](https://pyquil-docs.rigetti.com/en/stable/compiler.html#initial-rewiring)\nto the Quil compiler. For example:\n\n```python\nfrom qiskit_rigetti.hooks.pre_compilation import set_rewiring\n\n...\n\njob = execute(circuit, backend, shots=10, before_compile=[set_rewiring("NAIVE")])\n\n...\n```\n\n> **Note**: Rewiring directives require `quilc` version 1.25 or higher.\n\n##### `enable_active_reset`\n\nUse `enable_active_reset` to enable [active qubit reset](https://github.com/quil-lang/quil/blob/master/spec/Quil.md#state-reset),\nan optimization that can significantly reduce the time between executions. For example:\n\n```python\nfrom qiskit_rigetti.hooks.pre_execution import enable_active_reset\n\n...\n\njob = execute(circuit, backend, shots=10, before_execute=[enable_active_reset])\n\n...\n```\n\n## Development\n\n> **Note**: This module is developed in Python 3.7, other versions will currently fail type checking.\n\nDependencies are managed with [Poetry](https://python-poetry.org/) so you need to install that first. Once you\'ve installed all dependencies (`poetry install`) and activated the virtual environment (`poetry shell`), you can use these rules from the `Makefile` to run common tasks:\n\n1. Run tests: `make test`\n1. Check style and types: `make check-all`\n1. Check style only: `make check-style`\n1. Check types only: `make check-types`\n1. Reformat all code (to make `check-style` pass): `make format`\n1. Build documentation, serve locally, and watch for changes: `make watch-docs` (requires `docs` extra: `poetry install -E docs`)\n',
    'author': 'Rigetti Computing',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rigetti/qiskit-rigetti',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
