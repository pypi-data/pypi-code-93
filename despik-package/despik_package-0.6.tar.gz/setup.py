from setuptools import setup, find_packages

setup(name='despik_package',
      version='0.6',
      description='Some work with yfinance for self education',
      packages=['despik_package'],
      author_email='artomonik@gmail.com',
      install_requires=['yfinance', 'pandas', 'matplotlib', 'seaborn', 'sklearn']
      )