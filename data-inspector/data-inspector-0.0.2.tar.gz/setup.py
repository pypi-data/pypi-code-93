import setuptools


setuptools.setup(
    name='data-inspector',
    version='0.0.2',
    author="Kazi Amit Hasan",
    author_email="kaziamithasan89@gmail.com",
    description="This module brings different functions to make EDA, data cleaning easier.",
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
    License='MIT',
    long_description_content_type="text/markdown",
    url="",
    keywords='eda',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pandas','matplotlib','numpy', 'seaborn','scipy','warnings']
)