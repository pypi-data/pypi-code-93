"""
Pip.Services Postgres
------------------

Pip.Services is an open-source library of basic microservices.
pip_services3_postgres provides Postgres persistence components.

Links
`````

* `website <http://github.com/pip-services/pip-services>`_
* `development version <http://github.com/pip-services3-python/pip-services3-postgres-python>`

"""

try:
    readme = open('readme.md').read()
except:
    readme = __doc__

from setuptools import setup
from setuptools import find_packages

setup(
    name='pip_services3_postgres',
    version='3.2.1',
    url='http://github.com/pip-services3-python/pip-services3-postgres-python',
    license='MIT',
    author='Conceptual Vision Consulting LLC',
    author_email='seroukhov@gmail.com',
    description='Postgres persistence components for Pip.Services in Python',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['config', 'data', 'test']),
    include_package_data=True,
    zip_safe=True,
    platforms='any',
    install_requires=[
        'iso8601', 
        'PyYAML', 
        'psycopg2',
        'pip_services3_commons',
        'pip_services3_components',
        'pip_services3_data'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]    
)
