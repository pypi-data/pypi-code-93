# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['iometrics', 'iometrics.pytorch_lightning']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'iometrics',
    'version': '0.0.2',
    'description': 'Network and Disk I/O Stats Monitor',
    'long_description': '# iometrics\n\n[![Python](docs/img/badges/language.svg)](https://devdocs.io/python/)\n\nNetwork and Disk I/O Stats Monitor.\n\n## Usage\n\nMonitor and log Network and Disks statistics in MegaBytes per second.\n\n### Pytorch-lightning integration\n\n```py\n# TODO: add a pytorch-lightning integration example\n```\n\n### Pure-Python implementation\n\nQuick check:\n\n```sh\npython -c \'import iometrics; iometrics.usage()\'\n```\n\nFull code:\n\n```py\nimport time\nfrom iometrics import NetworkMetrics, DiskMetrics, DUAL_METRICS_HEADER\nnet  = NetworkMetrics()\ndisk = DiskMetrics()\nfor i in range(100):\n    time.sleep(1)\n    net.update_stats()\n    disk.update_stats()\n    print(DUAL_METRICS_HEADER) if i % 15 == 0 else None\n    row = (\n        f"| {net.mb_recv_ps.val:6.1f} | {net.mb_recv_ps.avg:6.1f} "\n        f"| {net.mb_sent_ps.val:5.1f} | {net.mb_sent_ps.avg:5.1f} "\n        f"| {int(disk.io_util.val):3d} | {int(disk.io_util.avg):3d} "\n        f"| {disk.mb_read.val:6.1f} | {disk.mb_read.avg:6.1f} "\n        f"| {disk.mb_writ.val:5.1f} | {disk.mb_writ.avg:5.1f} "\n        f"| {int(disk.io_read.val):4d} | {int(disk.io_read.avg):4d} "\n        f"| {int(disk.io_writ.val):3d} | {int(disk.io_writ.avg):3d} "\n        f"|"\n    )\n    print(row)\n```\n\n#### Example output\n\n```markdown\n|        Network (MBytes/s)       | Disk Util |            Disk MBytes          |           Disk I/O          |\n|     Received    |     Sent      |     %     |    MB/s Read    |  MB/s Written |     I/O Read    | I/O Write |\n|   val  |   avg  |  val  |  avg  | val | avg |  val   |  avg   |  val  |  avg  |   val  |   avg  | val | avg |\n| ------:| ------:| -----:| -----:| ---:| ---:| ------:| ------:| -----:| -----:| ------:| ------:| ---:| ---:|\n|    4.6 |    3.5 |   0.1 |   0.1 |  49 |   2 |   52.8 |    1.1 |   0.0 |   0.9 |    211 |      4 |   5 |  18 |\n|    4.1 |    3.5 |   0.1 |   0.1 |  61 |   3 |   60.4 |    2.4 |  40.3 |   1.7 |    255 |     10 | 149 |  21 |\n```\n\n## Contributing\n\nSee [CONTRIBUTING.md](CONTRIBUTING.md)\n',
    'author': 'Leo Gallucci',
    'author_email': 'elgalu3@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/elgalu/iometrics',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
