import os

import setuptools
from setuptools import setup
from jupyter_packaging import create_cmdclass


DATALAYER_VERSION = '0.0.6'


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
    add_data_files('jupytery_react/static')
    add_data_files('jupytery_react/templates')
    return data_files


cmdclass = create_cmdclass(
    data_files_spec=get_data_files()
)

setup_args = dict(
    name = 'jupytery_react',
    version = DATALAYER_VERSION,
    description = 'Jupytery React',
    packages = setuptools.find_packages(),
    long_description = open('README.md').read(),
    long_description_content_type='text/markdown',
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
             'jupytery-react = jupytery_react.application:main'
        ]
    },
)


if __name__ == '__main__':
    setup(**setup_args)
