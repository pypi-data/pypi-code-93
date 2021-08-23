from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='GamepayPy',
      version='1.0.0',
      description='Easy way to work with GamePay.best API',
      packages=['GamepayPy'],
      author_email='leetcrash.official@gmail.com',
      long_description=long_description,
    	 long_description_content_type='text/markdown',
    	 zip_safe=False)
