from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

setup(name='RR_dummy_distributions',
	version='0.2',
	description='Gaussian distributions',
	packages=['RR_dummy_distributions'],
	zip_safe=False,
	long_description=long_description,
	long_description_content_type='text/markdown'
)
