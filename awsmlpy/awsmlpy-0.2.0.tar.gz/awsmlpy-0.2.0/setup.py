from __future__ import print_function
from setuptools import setup, find_packages

setup(
    name='awsmlpy',
    version='0.2.0',
    description='Just wanna make sagemaker easy to use',
    licenes='MIT',
    packages=find_packages(),
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



from setuptools import setup

setup(
   name='awsmlpy',
   version='0.1.0',
   description='A useful module',
   author='LiuMing',
    author_email='2672790829@qq.com',
    packages=['awsmlpy'],  #same as name
   install_requires=['sagemaker==2.45.0',], #external packages as dependencies
)