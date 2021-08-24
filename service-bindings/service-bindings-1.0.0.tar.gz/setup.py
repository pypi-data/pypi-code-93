# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bindings']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'service-bindings',
    'version': '1.0.0',
    'description': 'A library to access [Service Binding Specification for Kubernetes](https://k8s-service-bindings.github.io/spec/) conformant Service Binding [Workload Projections](https://k8s-service-bindings.github.io/spec/#workload-projection).',
    'long_description': '# client-python\n\n[![Tests](https://github.com/nebhale/client-python/workflows/Tests/badge.svg?branch=main)](https://github.com/nebhale/client-python/actions/workflows/tests.yaml)\n[![codecov](https://codecov.io/gh/nebhale/client-python/branch/main/graph/badge.svg)](https://codecov.io/gh/nebhale/client-python)\n\n`client-python` is a library to access [Service Binding Specification for Kubernetes](https://k8s-service-bindings.github.io/spec/) conformant Service Binding [Workload Projections](https://k8s-service-bindings.github.io/spec/#workload-projection).\n\n## Example\n\n```python\nimport psycopg2 as psycopg2\n\nfrom bindings import bindings\n\nb = bindings.from_service_binding_root()\nb = bindings.filter(b, "postgresql")\n\nif len(b) != 1:\nraise ValueError("Incorrect number of PostgreSQL bindings: %s" % len(b))\n\nu = b[0].get("url")\nif u is None:\n    raise ValueError("No URL in binding")\n\nconn = psycopg2.connect(u)\n\n# ...\n\n```\n\n## License\n\nApache License v2.0: see [LICENSE](./LICENSE) for details.\n',
    'author': 'Ben Hale',
    'author_email': 'nebhale@nebhale.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nebhale/client-python',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
