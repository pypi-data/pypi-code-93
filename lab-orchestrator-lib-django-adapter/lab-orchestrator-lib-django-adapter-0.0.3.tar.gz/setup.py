import re
from setuptools import setup, find_packages
from os.path import abspath, dirname, join

CURDIR = dirname(abspath(__file__))

with open(join(CURDIR, 'lab_orchestrator_lib_django_adapter', '__init__.py'), "r", encoding="utf-8") as f:
    VERSION = re.search('^__version__ = "(.*)"', f.read()).group(1)
with open(join(CURDIR, 'README.md'), "r", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()
with open(join(CURDIR, 'requirements.txt'), "r", encoding="utf-8") as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name="lab-orchestrator-lib-django-adapter",
    version=VERSION,
    author="Marco Schlicht",
    author_email="git@privacymail.dev",
    description="An adapter to use the lab orchestrator lib in django projects.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/LabOrchestrator/LabOrchestratorLib-DjangoAdapter",
    license="MPL",
    project_urls={
        "Bug Tracker": "https://github.com/LabOrchestrator/LabOrchestratorLib-DjangoAdapter/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent"
    ],
    packages=["lab_orchestrator_lib_django_adapter", "lab_orchestrator_lib_django_adapter.migrations"],
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
)
