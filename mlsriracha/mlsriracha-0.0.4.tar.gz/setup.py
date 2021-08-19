from setuptools import find_packages, setup
setup(
    name='mlsriracha',
    version='0.0.4',
    description='A project to abstract the boilerplate required to deploy jobs in MLOps systems',
    author='Alex Chung',
    author_email='alex@socialg.tech',
    url='https://github.com/awcchungster/mlsriracha',
    packages=find_packages(),
    install_requires=[
        'google-cloud-storage>=1.40.0',
        'mlflow-skinny==1.19.0',
        'pandas==1.1.5',
        'boto3==1.18.1' 
    ],
)