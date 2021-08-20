from setuptools import setup, find_packages

setup(name='jsonrpcstdio',
      description='Asynchroncous Python implementation of JSON RPC for arbitrary'
                  ' Streams and a particular implementation for JSON RPC of '
                  'standard IO',
      author='amas0',
      version='0.6',
      packages=find_packages(),
      install_requires=[
          'aioconsole',
          'pydantic'
      ])
