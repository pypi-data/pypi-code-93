# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['powerk8s']
install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'kubernetes>=12.0.1,<13.0.0',
 'powerline-status>=2.7,<3.0']

setup_kwargs = {
    'name': 'powerk8s',
    'version': '0.2.0',
    'description': 'Powerline Segment for Kubernetes',
    'long_description': '# ☸️ powerk8s: Powerline Plugin for Kubernetes ☸️\n\n[![Actions Test Workflow Widget](https://github.com/gkze/powerk8s/workflows/CI/badge.svg)](https://github.com/gkze/powerk8s/actions?query=workflow%3Aci)\n[![PyPI Version](https://img.shields.io/pypi/v/powerk8s)](https://pypi.org/project/powerk8s/)\n[![Pdoc Documentation](https://img.shields.io/badge/pdoc-docs-green)](https://gkze.github.io/powerk8s/powerk8s.html)\n\nThis simple plugin is designed to show the Kubernetes cluster configured\nfor the current context in `$KUBECONFIG`.\n\nThis work is inspired by [so0k/powerline-kubernetes](https://github.com/so0k/powerline-kubernetes),\nand intends to be a drop-in **replacement** as well as an improvement upon the original work.\n\n## Installation\n\n```bash\n$ pip3 install powerk8s\n```\n\n## Configuration\n\nJust like with [so0k/powerline-kubernetes](https://github.com/so0k/powerline-kubernetes), you\'ll need a few things to get going:\n\n* **Colorschemes**\n\n  `~/.config/powerline/colorschemes/default.json`:\n\n  ```json\n  {\n    "groups": {\n      "kubernetes_cluster":         { "fg": "gray10", "bg": "darkestblue", "attrs": [] },\n      "kubernetes_cluster:alert":   { "fg": "gray10", "bg": "darkestred",  "attrs": [] },\n      "kubernetes_namespace":       { "fg": "gray10", "bg": "darkestblue", "attrs": [] },\n      "kubernetes_namespace:alert": { "fg": "gray10", "bg": "darkred",     "attrs": [] },\n      "kubernetes:divider":         { "fg": "gray4",  "bg": "darkestblue", "attrs": [] },\n    }\n  }\n  ```\n\n* **`powerk8s` invocation (& arguments)**\n\n  Here is a good starting point.\n  `~/.config/powerline/themes/shell/default.json`:\n\n  ```json\n  {\n    "function": "powerline_kubernetes.kubernetes",\n    "priority": 30,\n    "args": {\n        "show_kube_logo": true,\n        "show_cluster": true,\n        "show_namespace": true,\n        "show_default_namespace": false,\n        "alerts": [\n          "live",\n          "cluster:live"\n        ]\n    }\n  }\n  ```\n\n  This will add the segment to the shell.\n  Alternatively, placing this in `~/.config/powerline/colorschemes/default.json`\n  will make it show up in the Tmux status line.\n\n## Authors\n\n[@gkze](https://github.com/gkze)\n\n## License\n\n[MIT](LICENSE)\n',
    'author': 'George Kontridze',
    'author_email': 'george.kontridze@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gkze/powerk8s',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
