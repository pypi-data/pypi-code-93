from setuptools import setup, find_packages

INSTALL_REQUIRES = [
    'geopandas',
    'unidecode',
    'sparse_dot_topn',
    'dash',
    'pandas', 
    'plotly',
    'geopy==2.2.0', 
    'sklearn',
    'numpy',
    'scipy',
    'matplotlib',
    'requests' 


]

setup(
    name='geoapidata',
    packages=find_packages(exclude=["*test*"]),
    version='0.0.17',
    description='GeoAPI do TerraLab',
    author='TerraLab',
    install_requires= INSTALL_REQUIRES,
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
    package_data = {"GeoAPI": ['Data/*.csv', 'Data/*.xls'] },
)