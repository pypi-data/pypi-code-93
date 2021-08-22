# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gutsygit']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3', 'colorama>=0.4.4,<0.5.0']

entry_points = \
{'console_scripts': ['gg = gutsygit.main:run']}

setup_kwargs = {
    'name': 'gutsygit',
    'version': '0.6.0',
    'description': 'Command-line tool for fast git usage',
    'long_description': '# Gutsy Git\n\nMakes git usage extremely fast by making some gutsy assumptions.\n\n### Assumptions:\n\nYou work in a development environment based on pull request, avoiding pushing to your main branch. \nCommit messages are not always very relevant due to squashing. Your .gitignore is set up well enough to routinely add all changes.\n\n## Installation\n\n`pip install gutsygit`\n\n## Usage\n\n`gg <any number of single letter commands> [<arguments>]`\n\n### Commands:\n\n* `b [<name>]`: Create a new branch from origin/main with generated or given name, stashing and applying uncommitted changes if needed. \n   * If the branch exists, adds a numeric suffix to the name.\n* `s <name>`: Switch to existing branch.  \n* `c [<*message>]`: Commit changes. \n   * Ensures you are not on your protected branches by creating a branch if needed.\n   * Add all changes, including untracked files, and commit them with a generated or given commit message. \n   * If a `b` or `s` command remains after, argument(s) are assumed to be for the branch name, and the message is always generated.\n   * Retries once on failure to automatically commit changes resulting from pre-commit hooks.\n* `C [<*message>]`: Same as `c`, but bypasses pre-commit hooks on the second try using `--no-verify`.\n* `p`: Push commits.\n   * Potentially pulls from remote if needed.\n   * Sets tracking for the remote branch with the same name on the first push. \n* `P`: same as `p`, but opens a web browser if an url is returned by git, as GitHub does for pull requests.\n* `l`: Pull\n\n## Examples\n\n* `gg cP`: Commit and push changes with a generated commit message, and open a pull request page if suggested by the remote.\n* `gg bcp newbranch some description`: Create a new branch named "newbranch", commit, and push any changes that were not committed before this with the commit message "some description".\n* `gg Csl othertask`: Commit current changes regardless of commit hooks status, switch to \'othertask\' branch and updates it.\n\n## Settings\nSettings are retrieved from `git config` with the `gutsygit.[setting]` key:\n\n\n| Setting | Default value | Explanation |\n|---------|---------|-------------|\n|  protectedbranches | "main,master" | comma-separated list of branch names to avoid pushing to. Also used to branch from for a new clean branch, taking the first entry found that exists in the remote. |\n|  outputlevel | "0" | verbosity level (-1: debug, 1: headers/warnings/errors only) |\n\n\n',
    'author': 'Sander Land',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/sanderland/gutsygit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
