import setuptools
from setuptools import setup

with open('README.md') as fh:
    long_description = fh.read()


setup(
  name = 'intelli-sms-gateway',         # How you named your package folder (MyLib)
  long_description=long_description,
  long_description_content_type='text/markdown',
  version = '0.0.5.1',      # Start with a small number and increase it with every change you make
  license = 'MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A package extending developable features of the Intelli-Africa Solutions SMS Gateway',   # Give a short description about your library
  author = 'Intelli Africa Solutions',                   # Type in your name
  author_email = 'info@intelliafrica.solutions',      # Type in your E-Mail
  keywords = ['SMS', 'Bulk Sms', 'Bulk Email'],   # Keywords that define your package best
  py_modules=['intelli_gateway'],
  packages=setuptools.find_packages(),
  install_requires=[
          'requests',
          'pandas'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    "License :: OSI Approved :: MIT License", # Again, pick a license
    'Programming Language :: Python :: 3.6',
  ],
)