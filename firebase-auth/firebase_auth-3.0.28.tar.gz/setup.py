from setuptools import setup, find_packages

setup(
    name='firebase_auth',
    version='3.0.28',
    url='',
    description='A simple python wrapper for the Firebase API',
    author='',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='Firebase',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'requests>=2.20.0',
        'gcloud==0.17.0',
        'oauth2client==3.0.0',
        'requests-toolbelt!=0.9.0,>=0.8.0',
        'python_jwt==2.0.1',
        'pycryptodome==3.10.1'
    ]
)
