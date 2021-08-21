from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='OscarScrapper',
      version='0.1.0',
      description='Python Distribution Utilities',
      author='Yann Aubineau, Samuel Bozon',
      author_email='yann.aubineau@gmail.com, samuel.bozon@outlook.com',
      long_description=readme(),
      url='https://github.com/omasamo/Final-Project-JEM207',
      packages=find_packages("src"),  # include all packages under src
      package_dir={"": "src"},   # tell distutils packages are under src
      package_data= {"": ["data/corrections/*.csv"]},
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
      ],
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
