from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='VkStatusPy',
      version='1.01',
      description='Simple module for easy-working with VK Status',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author="LeetCrash",
      packages=['VkStatusPy'],
      author_email='leetcrash.official@gmail.com',
      zip_safe=False)
