import os
from setuptools import setup, find_packages

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    print (paths)
    return paths

setup(
    name='phobos_cli',
    version='0.1.0',
    py_modules=['phobos_cli'],
    install_requires=[
        'Click',
        'wheel'
    ],
    packages = find_packages(),
    package_data={'phobos': package_files('cookiecutter-phobos-project')},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'phobos = phobos_cli:cli',
        ],
    },
)