from setuptools import setup, find_packages
SERVICE_NAME = 'microservice-template-core'
SERVICE_NAME_NORMALIZED = SERVICE_NAME.replace('-', '_')

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

tests_require = [],

setup(
    name=SERVICE_NAME,
    version='2.2.14',
    description="Microservice template core",
    url='',
    include_package_data=True,
    author='',
    author_email='',
    classifiers=[
    ],
    keywords=[],
    packages=find_packages(),
    install_requires=requirements,
    tests_require=tests_require,
    entry_points={
        'console_scripts': [
            f'{SERVICE_NAME} = {SERVICE_NAME_NORMALIZED}.core:main',
        ]
    },
    zip_safe=False,
    cmdclass={},
    data_files=[]
)
