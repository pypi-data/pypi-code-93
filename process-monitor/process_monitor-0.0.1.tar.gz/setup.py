import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
setup(
    name='process_monitor',
    description='',
    version="0.0.1",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Mohammed Qudah',
    author_email='mohghq@gmail.com',
    package_dir={'process_monitor': 'process_monitor'},
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    tests_require=['tox'],
    classifiers=[],
    scripts=[]
)
