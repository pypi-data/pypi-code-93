from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='CKMobile',
    version='0.0.1b5',
    description='ChokChaisak',
    long_description=readme(),
    url='https://github.com/ChokChaisak/ChokChaisak',
    author='ChokChaisak',
    author_email='ChokChaisak@gmail.com',
    license='ChokChaisak',
    install_requires=[
        'matplotlib',
        'numpy',
        'uiautomator2>=2.13.0',
    ],
    keywords='CKMobile',
    packages=['CKMobile'],
    package_dir={
    'CKMobile': 'src/CKMobile',
    },
    package_data={
    'CKMobile': ['*'],
    },
)