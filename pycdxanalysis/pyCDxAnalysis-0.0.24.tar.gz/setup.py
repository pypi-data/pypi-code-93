from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))


def readme():
    with open('README.MD', 'r') as fh:
        return fh.read()


def get_version(rel_path: str):
    codes = ''
    with open(path.join(here, rel_path), 'r') as fh:
        codes = fh.read()

    for line in codes.splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"

            return line.split(delim)[1]
    else:
        raise RuntimeError('Unable to find version string')


setup(author='JaylanLiu',
      author_email='liujilong@genomics.cn',
      name='pyCDxAnalysis',
      version=get_version(f'{here}/pyCDxAnalysis/__init__.py'),
      description=
      'Integrative tools to anlysis companian diagnosis gene data set.',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='https://github.com/JaylanLiu/pyCDxAnalysis',
      packages=find_packages(),
      install_requires=['pandas>1.0', 'numpy', 'tableone', 'pyoncoprint','pypeta>=0.6.8'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ])
