from setuptools import setup

INSTALL_REQUIRES = [
    'geopandas',
    'unidecode',
    'sparse_dot_topn',
    'dash',
]

setup(
    name='geoapidata',
    packages=['GeoAPI'],
    version='0.0.6',
    description='GeoAPI do TerraLab',
    author='TerraLab',
    install_requires= INSTALL_REQUIRES,
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)