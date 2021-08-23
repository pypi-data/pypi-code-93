import pathlib
from setuptools import setup,find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# 
setup(
    name="awsee",
    version="0.0.25",
    description="Utility to help me manage my AWS profiles",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://ualter.github.io/awsee-site/",
    author="Ualter Otoni Pereira",
    author_email="ualter.junior@gmail.com",
    keywords = ['aws', 'cloud', 'awsee', 'boto3', 'ec2', 'vpc'],
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["awsee"],
    include_package_data=True,
    install_requires=[            
        'botocore>=1.17.63','boto3>=1.14.2','Pygments','arnparse','tinydb','clipboard','pyreadline','pytz','python-dateutil','XlsxWriter'
    ],
    scripts=[
        'shell_scripts/awsee.bat',
        'shell_scripts/awsee'
    ],
    entry_points={
        "console_scripts": [
            "awseepy=awsee.awseepy:main",
        ]
    },
)