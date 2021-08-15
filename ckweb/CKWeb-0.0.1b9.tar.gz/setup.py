from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='CKWeb',
    version='0.0.1b9',
    description='ChokChaisak',
    long_description=readme(),
    url='https://github.com/ChokChaisak/ChokChaisak',
    author='ChokChaisak',
    author_email='ChokChaisak@gmail.com',
    license='ChokChaisak',
    install_requires=[
        'matplotlib',
        'numpy',
        'robotframework-seleniumlibrary>=4.3.0',
        'webdriver-manager>=3.4.2',
        'keyboard>=0.13.5'
    ],
    keywords='CKWeb',
    packages=['CKWeb'],
    package_dir={
    'CKWeb': 'src/CKWeb',
    },
    package_data={
    'CKWeb': ['*','*/*'],
    },
)