import os

from setuptools import setup, Command, find_packages


class CleanCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info ./.pytest_cache ./.eggs')


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='amocrm-talenttech-oss',
    packages=find_packages(),
    version='0.2.5',
    license='MIT',
    description='Library for retrieving and uploading to database data from amocrm API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Dmitry Utiralov',
    author_email='d.utiralov@talenttech.ru',
    url='https://github.com/severgroup-tt/topmind-commons/tree/master/py/amocrm',
    install_requires=[
        'pandas==1.2.4',
        'etl-helper-talenttech==1.2.8',
        's3-talenttech-oss==0.0.8',
        'swap-inserter-talenttech-oss==0.0.3',
        'clickhouse-balanced-talenttech-oss==0.0.1',
        'requests',
        'vertica-connector-talenttech==1.1.3'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    cmdclass={
        'clean': CleanCommand
    }
)
