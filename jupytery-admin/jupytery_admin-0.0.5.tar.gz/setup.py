import os

from setuptools import setup, find_packages

from jupyter_packaging import create_cmdclass


pjoin = os.path.join

HERE = os.path.abspath(os.path.dirname(__file__))

DATALAYER_VERSION = '0.0.5'


share_jupytery_admin = pjoin(HERE, 'share', 'jupyterhub' 'jupytery-admin')


def get_package_data():
    """Get package data.
    """
    package_data = {}
    return package_data


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
    add_data_files('jupytery_admin/static')
    add_data_files('jupytery_admin/templates')
    "Get data files in share/jupyterhub/jupytery_admin"
    ntrim = len(HERE + os.path.sep)
    for (d, _, filenames) in os.walk(share_jupytery_admin):
        data_files.append((d[ntrim:], [pjoin(d, f)[ntrim:] for f in filenames]))
    return data_files


cmdclass = create_cmdclass(
    data_files_spec=get_data_files()
)


setup_args = dict(
    name = 'jupytery_admin',
    version = DATALAYER_VERSION,
    description = 'Jupyter Admin',
    long_description = open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires = '>=3.8',
    packages = find_packages(),
    package_data = get_package_data(),
    data_files = get_data_files(),
    install_requires = [
        'alembic',
        'jupyter_server',
        'jupyterhub>=1.4.1',
        'pluggy',
        'tornado>=6.0.4',
        'traitlets',
        'jinja2',
    ],
    extras_require = {
        'test': ['pytest'],
    },
    include_package_data=True,
    cmdclass = cmdclass,
    entry_points = {
        'console_scripts': [
             'jupytery-admin = jupytery_admin.application:main'
        ]
    },
)

if __name__ == '__main__':
    setup(**setup_args)
