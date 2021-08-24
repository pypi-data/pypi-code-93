#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='pandasio',
    version='0.0.2',
    description='Pandas to_sql/read_sql_query with primary/foreign key support',
    long_description='''PandasIO reimplements pandas.DataFrame.to_sql and
pandas.read_sql_query with more control over the SQL side of things
such as adding support for primary and foreign keys as well
serializing extra columns to JSON.''',
    long_description_content_type="text/markdown",
    author='Egil Moeller',
    author_email='em@emeraldgeo.no',
    url='https://github.com/EMeraldGeo/PandasIO',
    packages=setuptools.find_packages(),
    install_requires=[
        "pandas>=1.1",
        "sqlalchemy"
    ]
)

