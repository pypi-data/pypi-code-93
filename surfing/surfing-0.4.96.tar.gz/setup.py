from setuptools import setup, find_packages
from surfing import __version__

setup(
    name='surfing',
    version=__version__,
    description='backtest engine',
    author='puyuantech',
    author_email='info@puyuan.tech',
    packages=find_packages(),
    install_requires=[
        'pandas >= 0.25.1',
        'python-dateutil == 2.8.0',
        'boto3 >= 1.10.8',
        'requests >= 2.22.0',
        'scipy >= 1.3.0',
        'sklearn',
        'matplotlib',
        'statsmodels',
        'xlrd == 1.2.0',
        'cassandra-driver == 3.24.0',
        'numba == 0.48',
        's3fs == 0.4.2',
        'seaborn == 0.10.0',
        'SQLAlchemy >= 1.3.16',
        'PyMySQL >= 0.9.3',
        'psutil >= 5.7.2',
        'openpyxl >= 3.0.3',
        'tabulate >= 0.8.7',
        'pdfplumber >= 0.5.27',
        'html5lib >= 1.1',
        'openpyxl >= 3.0.3',
        'beautifulsoup4 >= 4.9.0',
        'bs4',
    ]
)

#python3 setup.py bdist_egg --exclude-source-files --dist-dir=../