from setuptools import setup
from os import path

# read the contents of README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

DEPENDENCIES = ['numpy', 'pandas', 'matplotlib==3.4.2',
                'scipy', 'seaborn', 'networkx', 'fury']

setup(name='braingraphgeo',
      version='0.4',
      description='Python package for performing analysis on structural brain networks using random geometric surrogate graphs',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Scott Trinkle',
      author_email='tscott.trinkle@gmail.com',
      license='MIT',
      install_requires=DEPENDENCIES,
      url='https://github.com/scott-trinkle/braingraphgeo',
      download_url='https://github.com/scott-trinkle/braingraphgeo/archive/refs/tags/v0.4.tar.gz',
      keywords=['tractography', 'brain network', 'graph theory'],
      packages=['braingraphgeo'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9'
      ]
      )
