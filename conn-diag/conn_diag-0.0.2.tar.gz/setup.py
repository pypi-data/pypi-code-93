from setuptools import setup
from setuptools import find_packages
from conn_diag import __version__
from conn_diag import __description__

setup(name='conn_diag',
      author='Muhannad Alghamdi',
      author_email='muhannadengineer@gmail.com',
      install_requires=['netrange==0.0.19', 'paramiko==2.7.2'],
      version=__version__,
      description=__description__,
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': ['conn-diag = conn_diag.__main__:main']
      })
