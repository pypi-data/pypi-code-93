from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: Financial and Insurance Industry',
    'Intended Audience :: Science/Research',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
]

setup(
    name='thirtysevena',
    description="37AUSTEN's Proprietary Algorithms Library.",
    url="https://github.com/37austen/37austen-python",
    author='37AUSTEN',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author_email='hello@37austen.com',
    license='MIT',
    classifiers=classifiers,
    keywords=['data analytics','finance', 'risk', 'market volatility'], 
    packages=find_packages(),
    install_requires=['requests==2.26.0']
)

