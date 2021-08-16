from setuptools import setup, find_packages

# pylint: disable=all
"""
python -m pip install --upgrade setuptools wheel twine
python setup.py sdist bdist_wheel

python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
python -m twine upload dist/*
"""

REQUIRED = [
    'aiohttp>=3.6.2',
    'aio_pika>=6.6.1',
    'simplejson>=3.17.2',
    'requests>=2.18.0',
    'ujson>=2.0.2',
    'envparse>=0.2.0',
    'vtb-py-logging>=1.0.6',
    'vtb-http-interaction'
]

setup(
    name='vtb-state-service-utils',
    version='1.7.2',
    packages=find_packages(exclude=['tests']),
    package_data={'': ['datafiles/*.json']},
    include_package_data=True,
    url='https://bitbucket.org/Michail_Shutov/state_service_utils',
    license='',
    author=' Mikhail Shutov',
    author_email='michael-russ@yandex.ru',
    description='utils for VTB state service',
    install_requires=REQUIRED,
    extras_require={
        'test': [
            'pytest',
            'pytest-env',
            'pytest-dotenv',
            'pytest-mock',
            'pylint',
            'pytest-asyncio'
        ]
    }
)
