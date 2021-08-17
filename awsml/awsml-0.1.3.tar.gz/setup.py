from __future__ import print_function
from setuptools import setup, find_packages

setup(
    name='awsml',
    version='0.1.3',
    description='Just wanna make sagemaker easy to use',
    licenes='MIT',
    packages=['awsml'],
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[
            'sagemaker==2.45.0',
    ],
    zip_safe=True,
)

