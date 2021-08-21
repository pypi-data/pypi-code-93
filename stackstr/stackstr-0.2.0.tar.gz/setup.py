from distutils.core import setup

setup(
    name='stackstr',
    packages=['stackstr', 'stackstr.common'],
    version='0.2.0',
    description='A small sdk to deploy your machine learning models right from your notebook',
    author='StackStr Engineering',
    author_email='founders@stackstr.io',
    url='https://stackstr.io',
    keywords=['stackstr', 'machine learning', 'infrastructure'],
    install_requires=[
        'certifi',
        'chardet',
        'idna',
        'joblib',
        'requests',
        'urllib3'
    ],
)
