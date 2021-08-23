import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pcpt-cde',
    version='0.6',
    author='surajthapa@pingidentity.com',
    author_email='surajthapa@pingidentity.com',
    license='2021 Ping',
    description='Utility tool for the pingcloud cde environment',
    packages=setuptools.find_packages(),
    py_modules=[
        'pcpt-cde',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3',
    package_dir={'': 'src'},
    install_requires=[
        'boto3>=1.17.18',
        'prettytable>=1.0.1',
        'configparser>=5.0.2'
    ]
)
