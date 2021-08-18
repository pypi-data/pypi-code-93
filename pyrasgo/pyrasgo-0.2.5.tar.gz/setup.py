from setuptools import setup
import os

_here = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(_here, 'pyrasgo', 'version.py')) as f:
    exec(f.read(), version)

with open(os.path.join(_here, 'DESCRIPTION.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyrasgo',
    version=version['__version__'],
    description=('Alpha version of the Rasgo Python interface.'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Patrick Dougherty',
    author_email='patrick@rasgoml.com',
    url='https://www.rasgoml.com/',
    license='MPL 2.0',
    packages=['pyrasgo',
              'pyrasgo.api',
              'pyrasgo.primitives',
              'pyrasgo.schemas',
              'pyrasgo.storage',
              'pyrasgo.storage.dataframe',
              'pyrasgo.storage.datawarehouse',
              'pyrasgo.utils'],
    install_requires=[
        # Note these are duplicated in requirements.txt
        "more-itertools",
        "pandas",
        "pydantic",
        "pyyaml",
        "requests",
        "tqdm",
        "snowflake-connector-python>=2.4.0",
        "snowflake-connector-python[pandas]",
        "idna>=2.5,<3",
        "pyarrow>=3.0.0,<4"
    ],
    extras_require={
        "df":  [
            "shap", 
            "catboost"
        ],
        "snowflake":  [
            "snowflake-connector-python>=2.4.0",
            "snowflake-connector-python[pandas]",
            "idna>=2.5,<3",
            "pyarrow>=3.0.0,<4"
        ],
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.7'],
)
