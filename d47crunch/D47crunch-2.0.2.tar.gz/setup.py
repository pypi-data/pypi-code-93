# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['D47crunch']

package_data = \
{'': ['*']}

install_requires = \
['lmfit>=1.0.2,<2.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'numpy>=1.21.1,<2.0.0',
 'scipy>=1.7.0,<2.0.0']

setup_kwargs = {
    'name': 'D47crunch',
    'version': '2.0.2',
    'description': 'Standardization and analytical error propagation of Δ47 and Δ48 clumped-isotope measurements',
    'long_description': "# D47crunch\n\n[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4314550.svg)](https://doi.org/10.5281/zenodo.4314550)\n\nPython library for processing and standardizing carbonate clumped-isotope analyses, from low-level data out of a dual-inlet mass spectrometer to final, “absolute” Δ<sub>47</sub> and Δ<sub>48</sub> values with fully propagated analytical error estimates.\n\n## Documentation\n\nFor the full API and a short tutorial, see [https://mdaeron.github.io/D47crunch].\n\n[https://mdaeron.github.io/D47crunch]: https://mdaeron.github.io/D47crunch\n\n## Installation\n\nThis should do the trick:\n\n```bash\npip install D47crunch\n```\n\nAlternatively:\n\n1. download the [dev branch] or the [latest release] and unzip it\n2. rename the resulting directory to `D47crunch`\n3. chose one of one of the following options:\n\t+ move the `D47crunch` directory to somewhere in your Python path\n\t+ move the `D47crunch` directory to your desired working directory\n\t+ move the `D47crunch` directory to any other location (e.g., `/foo/bar`) and include the following code snippet in your scripts:\n\n```py\nimport sys\nsys.path.append('/foo/bar')\n```\nHaving done any of the above you should now be able to `import D47crunch`, with the following requirements: [Python 3], [numpy], [matplotlib], [scipy], and [lmfit].\n\n[Python 3]: https://www.python.org\n[numpy]: https://numpy.org\n[lmfit]: https://lmfit.github.io\n[matplotlib]: https://matplotlib.org\n[scipy]: https://www.scipy.org\n[dev branch]: https://github.com/mdaeron/D47crunch/archive/dev.zip\n[latest release]: https://github.com/mdaeron/D47crunch/releases/latest\n\n## Contact\n\nAll questions and suggestions are welcome and should be directed at [Mathieu Daëron](mailto:daeron@lsce.ipsl.fr?subject=[D47crunch]).\n\n",
    'author': 'Mathieu Daëron',
    'author_email': 'mathieu@daeron.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mdaeron/D47crunch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
