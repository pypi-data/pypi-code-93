import time
from distutils.core import setup


setup(version=time.strftime('%y%m%d'),
      install_requires=['bs4', 'lxml', 'requests'],
      description='Rank Nifty500 stocks on Quality, Growth and Value',
      name='magicrank',
      packages=['magicrank'])

# python3 setup.py sdist upload
