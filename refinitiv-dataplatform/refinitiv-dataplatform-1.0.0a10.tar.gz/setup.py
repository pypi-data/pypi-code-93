# coding: utf-8

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import re


# NoseTestCommand allow to launch nosetest with the command 'python setup.py test'
class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose

        nose.run_exit(argv=["nosetests"])


module_file = open("refinitiv/dataplatform/__init__.py").read()
metadata = dict(re.findall('__([a-z]+)__\s*=\s*"([^"]+)"', module_file))


# this_directory = path.abspath(path.dirname(__file__))
# with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
#     long_description = f.read()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="refinitiv-dataplatform",
    version=metadata["version"],
    description="Python package for retrieving data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://developers.refinitiv.com/refinitiv-data-platform/refinitiv-data-platform-libraries",
    author="REFINITIV",
    author_email="",
    license="Apache 2.0",
    data_files=[("", ["LICENSE.md", "CHANGES.txt"])],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={"": ["rdplibconfig.default.json"]},
    zip_safe=False,
    python_requires=">3.6",
    install_requires=[
        "requests-async>=0.6.2",
        "httpx",
        "nest_asyncio",
        "datetime",
        "validators",
        "pandas>=1.0.0",
        "numpy>=1.11.0",
        "appdirs>=1.4.3",
        "python-dateutil",
        "websocket-client>=0.54.0,!=1.0.0",
        "deprecation",
        "python-configuration>=0.7.1,!=0.8.0",
        "eventemitter>=0.2.0",
        "watchdog>=0.10.2",
        "scipy",
    ],
    test_suite="nose.collector",
    tests_require=["nose", "mock", "coverage"],
    cmdclass={"test": NoseTestCommand},
)
