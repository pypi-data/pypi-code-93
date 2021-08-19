from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='flintypy',
    version='0.0.0',
    description='Flexible and Interpretable Non-parametric Tests '
                'of Exchangeability',
    author='Alan Aw, Jeffrey Spence',
    author_email='alanaw1@berkeley.edu, jspence@stanford.edu',
    license='GPLv3',
    packages=['flintypy'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    zip_safe=False,
    install_requires=[
        'pytest',
        'gmpy2',
        'numpy>=1.16.5',
        'scipy>=1.5.0',
        'numba>=0.53.0'
    ]
)
