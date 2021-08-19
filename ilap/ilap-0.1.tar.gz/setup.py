import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='ilap',
      version='0.1',
      description='Numerical Laplace transform inversion tools',
      author='Scott K. Hansen',
      author_email='skh@bgu.ac.il',
      install_requires=['numpy','mpmath'],
      license_files=('LICENSE.txt',),
      long_description=read('README.md'),
      long_description_content_type='text/markdown',
      packages=['ilap'],
      url='https://gitlab.com/scottkalevhansen/ilap',
      zip_safe=True)