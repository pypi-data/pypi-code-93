from setuptools import setup, find_packages

setup(
   name='johnshopeetools',
   version='0.1.14',
   author='John Chan | making difficult live easier',
   author_email='john.chanky@seamoney.com',
   packages=find_packages(),
   description='A toolbox for credit policy analysis',
   install_requires=[
       "pandas",
   ],
)