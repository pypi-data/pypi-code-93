from setuptools import setup, find_packages

setup(name='despik_package',
      version='0.4',
      description='Some work with yfinance for self education',
      packages=find_packages(),
      author_email='artomonik@gmail.com',
      install_requires=['yfinance', 'pandas', 'matplotlib', 'seaborn', 'sklearn']
      )