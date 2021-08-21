from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='price_process',
      version='1.0',
      description='Library for generating various stochastic price sequences ',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/borab96/price_process',
      author='Bora Basa',
      author_email='borabasa@gmail.com',
      keywords=['finance','stochastic process','mathematical finance','SDE','investing', 'trading'],
      license='MIT',
      python_requires='>=3',
      requires=['numpy', 'scipy', 'matplotlib'],
      install_requires=['numpy', 'scipy', 'matplotlib'],
      zip_safe=False)
