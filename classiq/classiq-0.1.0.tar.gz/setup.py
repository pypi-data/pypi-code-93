# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['classiq', 'classiq.authentication']

package_data = \
{'': ['*']}

install_requires = \
['ConfigArgParse>=1.5,<2.0',
 'Pyomo>=6.0.1,<7.0.0',
 'httpx>=0.18.2,<0.19.0',
 'keyring>=23.0.1,<24.0.0',
 'more-itertools>=8.7.0,<9.0.0',
 'networkx>=2.5.1,<3.0.0',
 'numpy>=1.20.1,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'qiskit>=0.29.0,<0.30.0',
 'websockets>=9.1,<10.0']

setup_kwargs = {
    'name': 'classiq',
    'version': '0.1.0',
    'description': 'Classiq SDK Package',
    'long_description': 'Classiq enables the development of quantum circuits and algorithms that could not be created otherwise. \n\nWe do this by synthesizing high-level functional models into optimized quantum circuits, taking into account the\nconstraints that are important to the designer. Furthermore, we are able to generate circuits for practically any\nuniversal gate-based quantum computer and are compatible with most quantum cloud providers.\n\n## Requirements\nPython 3.8+\n\n\n## Installation\n```console\n$ pip install classiq\n```\n\n## Example\n\n```python\nimport asyncio\n\nfrom classiq.generator import Generator\nfrom classiq.analyzer import Analyzer\nfrom classiq_interface.generator.state_preparation import (\n    StatePreparation,\n    PMF,\n    StatePreparationOutputs,\n)\nfrom classiq_interface.generator.qft import QftInputs, QFT\nfrom classiq_interface.generator.preferences.optimization import (\n    Optimization,\n    OptimizationType,\n)\n\ncircuit_generator = Generator(qubit_count=8, max_depth=20)\nopt = Optimization(optimization_type=OptimizationType.DEPTH, approximation_error=0.05)\ncircuit_generator.constraints.optimization = opt\n\nprobabilities = (0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125)\npmf = PMF(pmf=probabilities)\nsp_params = StatePreparation(probabilities=pmf, num_qubits=5)\nsp_out_wires = circuit_generator.StatePreparation(params=sp_params)\n\nout_wire_enum = StatePreparationOutputs.OUT\nin_wire_enum = QftInputs.IN\nwire = sp_out_wires[out_wire_enum]\n\nqft_params = QFT(num_qubits=5)\ncircuit_generator.QFT(params=qft_params, in_wires={in_wire_enum: wire})\n\ncircuit = asyncio.run(circuit_generator.generate())\n\ncircuit_analyzer = Analyzer(circuit=circuit)\nanalysis_result = asyncio.run(circuit_analyzer.analyze())\n\n```\n\n## License\n\n',
    'author': 'Classiq Technologies',
    'author_email': 'support@classiq.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://classiq.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
