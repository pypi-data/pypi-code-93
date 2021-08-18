import os

from setuptools import find_packages, setup

__VERSION__ = '1.0.7'

with open('README.md', 'r') as fh:
    long_description = fh.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='AX3 Email',
    version=__VERSION__,
    packages=find_packages(),
    description='A Django app to send emails using Huey tasks',
    long_description_content_type='text/markdown',
    long_description=long_description,
    url='https://github.com/Axiacore/ax3-email-backend',
    author='Axiacore, ',
    author_email='info@axiacore.com',
    include_package_data=True,
    install_requires=[
        'django >= 3.1.5',
        'huey >= 2.3.0',
        'premailer >= 3.7.0',
    ]
)
