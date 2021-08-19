from setuptools import setup, version
from setuptools import find_packages

setup(
    name = 'celebrity_birth_test',
    version = '0.0.1',
    description = 'Package that will help find celeb birthdays',
    url = 'https://github.com/MilanSajiv/Celebrities-Births/tree/main/Celebrities_Births/project',
    author = 'Milan Sajiv',
    author_email = 'milansajiv@hotmail.co.uk',
    license = 'MIT',
    packages = find_packages(),
    install_requires = ['requests', 'beautifulsoup4']
)