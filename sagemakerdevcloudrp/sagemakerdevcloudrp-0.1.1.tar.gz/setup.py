
from setuptools import setup

setup(
      name='sagemakerdevcloudrp',    # This is the name of your PyPI-package.
      keywords='sagemaker',
      version='0.1.1',
      description='The Sagemaker client to run outside the AWS environment.',
      long_description=open('README.txt').read(),
      scripts=['code.py']                  # The name of your scipt, and also the command you'll be using for calling it
)
        