from setuptools import setup, find_packages
from os import path

HERE = path.abspath(
    path.dirname(__file__)
)

ROOT_PACKAGE = 'convisoappsec'
SCRIPTS_SHELL_COMPLETER_DIR = path.join('scripts', 'shell_completer')
VERSION_MODULE = path.join(ROOT_PACKAGE, 'version.py')
README_PATH = path.join(HERE, 'README.md')

version_module_context = {}

with open(VERSION_MODULE) as fp:
    exec(fp.read(), version_module_context)

with open(README_PATH, "r") as fh:
    long_description = fh.read()


version = version_module_context.get('__version__')


setup(
    name='conviso-flowcli',
    version=version,
    long_description=long_description,
    long_description_content_type='text/markdown',
    maintainer='Jean Carlos Sales Pantoja',
    maintainer_email='jpantoja@convisoappsec.com',
    packages=find_packages(
        exclude=["test*"],
    ),
    install_requires=[
        "GitPython>=3.1.2,<4",
        "click>=7.1.2,<8",
        "requests>=2.23.0,<3",
        "semantic-version>=2.8.5,<3",
        "docker>=4.2.1,<5",
        "PyYAML>=5.3.1,<6",
        "click-log>=0.3.2,<1",
        "transitions>=0.8.7,<1",
        "jsonschema>=2.5.1,<3"
    ],
    entry_points='''
        [console_scripts]
        flow=convisoappsec.flowcli.entrypoint:cli
    ''',
    scripts=[
        path.join(SCRIPTS_SHELL_COMPLETER_DIR, 'flow_bash_completer.sh'),
        path.join(SCRIPTS_SHELL_COMPLETER_DIR, 'flow_zsh_completer.sh'),
        path.join(SCRIPTS_SHELL_COMPLETER_DIR, 'flow_fish_completer.fish'),
    ],
    python_requires='>=3.4',
)
