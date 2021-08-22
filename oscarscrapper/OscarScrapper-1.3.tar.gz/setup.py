from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

setup(name='OscarScrapper',
      version='1.3',
      long_description = long_description,
      long_description_content_type='text/markdown',
      description='Academy Awards Scraper and Data processor',
      author='Yann Aubineau, Samuel Bozon',
      author_email='yann.aubineau@gmail.com, samuel.bozon@outlook.com',
      url='https://github.com/omasamo/Final-Project-JEM207',
      packages=find_packages("src"),  # include all packages under src
      package_dir={"": "src"},   # tell distutils packages are under src
      package_data= {"": ["data/corrections/*.csv"]},
      install_requires=[
          'markdown',
          'requests',
          'tdqm',
          'scrapy',
          'pandas',
          'numpy',
          'jellyfish'
      ],
     )
