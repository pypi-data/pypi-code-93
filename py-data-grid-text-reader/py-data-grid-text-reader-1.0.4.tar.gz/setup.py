from setuptools import setup, find_packages

with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()

requirements = ["sqlalchemy>=1"]

setup(
    name='py-data-grid-text-reader',
    version='1.0.4',
    author='Steve Whalen',
    author_email='sjwhalen@yahoo.com',
    description=('Reads a string representing a database record set and '
                 'converts it to a different representation, such as a list '
                 'of dictionaries or a set of SQL CREATE TABLE and INSERT '
                 'statements that can be used to persist the data to a '
                 'database.'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/datagridreader/py-data-grid-text-reader/',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.6',
)
