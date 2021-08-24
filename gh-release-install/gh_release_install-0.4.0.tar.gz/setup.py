# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gh_release_install']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0', 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['gh-release-install = gh_release_install.cli:run']}

setup_kwargs = {
    'name': 'gh-release-install',
    'version': '0.4.0',
    'description': 'CLI helper to install Github releases on your system.',
    'long_description': '# Github release installer\n\n[![CI](https://github.com/jooola/gh-release-install/actions/workflows/ci.yml/badge.svg)](https://github.com/jooola/gh-release-install/actions/workflows/ci.yml)\n[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/gh-release-install.svg)](https://pypi.org/project/gh-release-install/)\n[![PyPI Package Version](https://img.shields.io/pypi/v/gh-release-install.svg)](https://pypi.org/project/gh-release-install/)\n\n`gh-release-install` is a CLI helper to install Github releases on your system.\nIt can be used for pretty much anything, to install a formatter in your CI, deploy\nsome binary using an orcherstration tool, or on your desktop.\n\nThis project was mainly created to...\n\n```sh\n# ...turn this mess:\nwget --quiet --output-document=- "https://github.com/koalaman/shellcheck/releases/download/v0.7.1/shellcheck-v0.7.1.linux.x86_64.tar.xz" \\\n    | tar --extract --xz --directory=/usr/local/bin --strip-components=1 --wildcards \'shellcheck*/shellcheck\' \\\n    && chmod +x /usr/local/bin/shellcheck\n\nwget --quiet --output-document=/usr/local/bin/shfmt "https://github.com/mvdan/sh/releases/download/v3.2.1/shfmt_v3.2.1_linux_amd64"\xa0\\\n    && chmod +x /usr/local/bin/shfmt\n\n# Into this:\npip3 install gh-release-install\n\ngh-release-install \\\n      "koalaman/shellcheck" \\\n      "shellcheck-{tag}.linux.x86_64.tar.xz" --extract "shellcheck-{tag}/shellcheck" \\\n      "/usr/bin/shellcheck"\n\ngh-release-install \\\n      "mvdan/sh" \\\n      "shfmt_{tag}_linux_amd64" \\\n      "/usr/bin/shfmt"\n```\n\nFeatures:\n\n- Download releases from Github.\n- Extract zip or tarball on the fly.\n- Pin to a desired version or get the `latest` version.\n- Keep track of the local tools version using a version file.\n\n## Installation\n\nInstall the package from pip:\n\n```sh\npip install gh-release-install\ngh-release-install --help\n```\n\nOr with with pipx:\n\n```sh\npipx install gh-release-install\ngh-release-install --help\n```\n\n## Usage\n\n```sh\nUsage: gh-release-install [OPTIONS] REPOSITORY ASSET DESTINATION\n\n  Install GitHub release file on your system.\n\n  The REPOSITORY argument define the Github REPOSITORY org/repo to get the\n  release from.\n\n  Examples:\n      mvdan/sh\n      prometheus/prometheus\n\n  The ASSET argument define the release ASSET filename. Note that ASSET may\n  contain variables such as \'{version}\' or \'{tag}\'.\n\n  Examples:\n      shfmt_{tag}_linux_amd64\n      prometheus-{version}.linux-amd64.tar.gz\n\n  The DESTINATION argument define the DESTINATION path for the downloaded\n  file. Note that DESTINATION may contain variables such as \'{version}\' or\n  \'{tag}\'.\n\n  Examples:\n      /usr/bin/local/shfmt\n      /opt/prometheus/prometheus\n\n  If the release asset is an archive, use the --extract flag to extract the\n  <filename> from the archive and install the extracted file instead. Note\n  that <filename> may contain variables such as \'{version}\' or \'{tag}\'.\n\n  Examples:\n      --extract prometheus-{version}.linux-amd64/prometheus\n\n  To install a specific version, use the --version flag to set the desired\n  version. With \'latest\' the installer will ask the Github API to find the\n  latest version. The default is \'latest\'.\n\n  Examples:\n      latest\n      v2.28.1\n\n  To track the version installed on the system, use the --version-file flag to\n  define the <filename> where the version should be saved. The default is not\n  to save this version file. Note that <filename> may contain variables such\n  as \'{destination}\'.\n\n  Examples:\n      --version-file /opt/versions/prometheus.version\n      --version-file {destination}.version\n\n  Some full examples:\n\n  gh-release-install \\\n      \'mvdan/sh\' \\\n      \'shfmt_{tag}_linux_amd64\' \\\n      \'/usr/bin/local/shfmt\' \\\n      --version \'v3.3.1\'\n\n  gh-release-install \\\n      \'prometheus/prometheus\' \\\n      \'prometheus-{version}.linux-amd64.tar.gz\' \\\n      --extract \'prometheus-{version}.linux-amd64/prometheus\' \\\n      \'/usr/local/bin/prometheus\' \\\n      --version-filename \'{destination}.version\'\n\nOptions:\n  --extract <filename>       Archive member to extract.\n  --version <version>        Release version to install.\n  --version-file <filename>  File to track the version installed.\n  --help                     Show this message and exit.\n\n```\n',
    'author': 'Joola',
    'author_email': 'jooola@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
