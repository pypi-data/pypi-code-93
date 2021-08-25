import os

from setuptools import setup
from jupyter_packaging import create_cmdclass


DATALAYER_VERSION = '0.0.5'


def get_data_files():
    """Get the data files for the package.
    """
    data_files = [
        ('etc/jupyter/jupyter_server_config.d', 'etc/jupyter/jupyter_server_config.d/', '*.json'),
    ]
    def add_data_files(path):
        for (dirpath, dirnames, filenames) in os.walk(path):
            if filenames:
                paths = [(dirpath, dirpath, filename) for filename in filenames]
                data_files.extend(paths)
    # Add all static and templates folders.
    add_data_files('jupytery_federation/static')
    add_data_files('jupytery_federation/templates')
    return data_files


cmdclass = create_cmdclass(
    data_files_spec=get_data_files()
)

setup_args = dict(
    name = 'jupytery_federation',
    version = DATALAYER_VERSION,
    description = 'Jupytery Federation',
    long_description = open('README.md').read(),
    python_requires = '>=3.8',
    install_requires = [
        'jupyter_server',
        'jinja2',
    ],
    extras_require = {
        'test': ['pytest'],
    },
    include_package_data=True,
    cmdclass = cmdclass,
    entry_points = {
        'console_scripts': [
             'jupytery-federation = jupytery_federation.application:main'
        ]
    },
)


if __name__ == '__main__':
    setup(**setup_args)
