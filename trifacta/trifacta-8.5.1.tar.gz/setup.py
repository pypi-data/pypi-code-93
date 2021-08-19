from setuptools import setup, find_packages

from trifacta.version import __version__


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='trifacta',
    version=__version__,
    description='Python SDK for Trifacta',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://www.trifacta.com',
    author='Trifacta Inc',
    author_email='support@trifacta.com',
    keywords='dataprep preparation wrangle wrangling wrangler trifacta',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'pandas>=1.1.2',
        'numpy>=1.17.0',
        'requests>=2.22.0',
        'regex>=2020.10.11',
        'python-slugify>=4.0.1',
        'tqdm>=4.55.1',
        'boto3>=1.17.25',
        'ipywidgets>=7.6.3',
        'ijson>=3.1.4',
        'simplejson>=3.16.0',
        'pywebhdfs>=0.4.1',
        'metaphone>=0.6',
        'python-slugify>=4.0.1',
    ],
    python_requires='>3.6, < 3.9'
)
