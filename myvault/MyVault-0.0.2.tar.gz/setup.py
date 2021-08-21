# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['myvault', 'myvault.statics', 'myvault.utils']

package_data = \
{'': ['*'], 'myvault': ['sql/*']}

install_requires = \
['click>=8.0,<9.0',
 'colorama>=0.4.4,<0.5.0',
 'pycryptodome>=3.10,<4.0',
 'pyperclip>=1.8,<2.0']

entry_points = \
{'console_scripts': ['myvault = myvault.cli:commands']}

setup_kwargs = {
    'name': 'myvault',
    'version': '0.0.2',
    'description': 'A simple, offline vault to store secrets e.g. your password.',
    'long_description': '# MyVault\n\nA simple, offline vault to store secrets e.g. your password.\n\n* SQLite database is used for storage.\n* Each secret is AES-256 encrypted using an SHA-256 hash generated from a key*, salt*, and iterations*.\n* The decrypted secret can only be copied to the clipboard*.\n* Secrets are never displayed, logged, or uploaded anywhere.\n\n*\\*: Should be [configured](#configuration).*\n\n## Installation with pip\n\nRequirement: Python 3.7+\n\n### Source: PyPi\n```bash\n$ pip3 install MyVault\n```\n\n## Configuration\n\nConfiguration for the encryption is provided as a *cfg* file.\n\nExample: [cipher_example.cfg](cipher_example.cfg)\n```buildoutcfg\n[cipher]\nkey = replace-me\nsalt = replace-me\niterations = 100000\nclipboard_ttl = 15\n```\n\nNotes:\n* `key`: Key, a hash of which is used for encryption.\n* `salt`: Salt for hashing.\n* `iterations`: Iterations for hashing.\n* `clipboard_ttl`: Seconds to retain copied secret in the clipboard.\n\n## Usage\n\n### Commands\n\n#### General\n\n* See available commands:\n    ```bash\n    $ myvault --help\n    Usage: myvault [OPTIONS] COMMAND [ARGS]...\n\n    Options:\n      --help  Show this message and exit.\n\n    Commands:\n      add     Add a secret (will be prompted) to the vault.\n      copy    Copy the decrypted secret from the vault to the clipboard.\n      remove  Delete either a secret by its folder and name.\n      list    List all the folders and names of secrets.\n      update  Update encryption configuration for the vault.\n    ```\n\n* Help for a specific command: `$ myvault <command> --help`\n\n  Example:\n    ```bash\n    $ myvault add --help\n    Usage: myvault add [OPTIONS] NAME [FOLDER]\n\n      Add a secret (will be prompted) to the vault.\n\n    Options:\n      --config FILE  Path to the encryption config file.  [required]\n      --db FILE      Path to the vault database.  [required]\n      --help         Show this message and exit\n    ```\n\n#### Add a secret\n\nIf the vault database does not exist, it will be created. After the following command is run, you will see a prompt to enter the secret.\n```bash\n$ myvault add --db=<path_to_sqlite3_file> --config=<path_to_config_file> instagram social-media\n```\n\n#### List secrets\n\nAll the folders and names of secrets will be listed.\n```bash\n$ myvault list --db=<path_to_sqlite3_file> --config=<path_to_config_file>\n```\n\n#### Copy a secret\n\nCopy the decrypted secret from the vault to the clipboard.\n```bash\n$ myvault copy --db=<path_to_sqlite3_file> --config=<path_to_config_file> instagram social-media\n```\n\n#### Remove a secret\n\nDelete a secret by its folder and name.\n```bash\n$ myvault remove --db=<path_to_sqlite3_file> --config=<path_to_config_file> instagram social-media\n```\n\n#### Update encryption configuration\n\nUpdate encryption configuration for the vault.\n```bash\n$ myvault update --db=<path_to_sqlite3_file> --config=<path_to_config_file> <path_to_new_config_file>\n```\n\n:warning: Make sure to pass the correct path to `--config` once the encryption config is updated. Otherwise, `copy` could either return an empty string `""` or exit with the status `INVALID_CONFIG_ERROR`.\n\n### Recommendations\n\n1. Use an external drive to store the vault database, as well as the config file so that the vault is **isolated and mobile**.\n1. Create aliases so that the **CLI commands are shortened**.\n   1. Add the following lines in *shell profile*:\n        ```text\n        MYVAULT_DB="<absolute_path_to_db>"\n        MYVAULT_CONFIG="<absolute_path_to_config>"\n        alias vault-ad="myvault add --db=$MYVAULT_DB --config=$MYVAULT_CONFIG"\n        alias vault-cp="myvault copy --db=$MYVAULT_DB --config=$MYVAULT_CONFIG"\n        alias vault-ls="myvault list --db=$MYVAULT_DB --config=$MYVAULT_CONFIG"\n        alias vault-up="myvault update --db=$MYVAULT_DB --config=$MYVAULT_CONFIG"\n        alias vault-rm="myvault remove --db=$MYVAULT_DB --config=$MYVAULT_CONFIG"\n        ```\n   1. Shortened cli commands:\n       ```bash\n       $ vault-ad insta social_media\n       $ vault-cp insta social_media\n       $ vault-ls\n       $ vault-rm insta social_media\n       $ vault-up /Volumes/external/new_config.cfg\n       ```\n\n## Author\n\n**&copy; 2021, [Samyak Tamrakar](https://www.linkedin.com/in/srtamrakar/)**.\n',
    'author': 'Samyak Tamrakar',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/srtamrakar/vault',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
