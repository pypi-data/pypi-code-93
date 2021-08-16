"""
setup.py 

Information used to build the package
"""
from setuptools import find_namespace_packages, setup
import os
import subprocess


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


def get_version():
    ENV = os.environ['ENV'] # Must be set
    tag = subprocess.check_output(
        ['git', 'describe', '--tags', '--exact-match'],
        encoding='UTF-8'
    ).rstrip()
    if ENV in ['dev', 'test']:
        version = '0.' + tag
    elif ENV == 'prod':
        version = '1.' + tag
    else:
        raise ValueError(f"Unknown environment {ENV}")
    return version


setup(
    name="akerbp.mlops", 
    version=get_version(),
    author="Alfonso M. Canterla",
    author_email="alfonso.canterla@soprasteria.com",
    description="MLOps framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/akerbp/mlops/",
    packages=find_namespace_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "cognite-sdk-experimental>=0.34.0", 
        "pytest>=6.1.1",
        "pydantic>=1.7.3",
        "PyYAML==5.4.1"
    ],
    scripts=[
        'src/akerbp/mlops/deployment/deploy_training_service.sh', 
        'src/akerbp/mlops/deployment/deploy_prediction_service.sh',
        'src/akerbp/mlops/gc/install_gc_sdk.sh'
    ],
    include_package_data=True,
    package_data={'': [
        'mlops/gc/Dockerfile', 
        'mlops/gc/requirements.app',
        'mlops/gc/install_req_file.sh',
        'mlops/deployment/bitbucket-pipelines.yml' 
        ]},
)