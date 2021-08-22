from setuptools import setup, find_packages


with open("requirements.txt", encoding="utf-8") as f:
    REQUIRED = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

with open("VERSION", "r", encoding="utf-8") as fh:
    VERSION = fh.read()

setup(
    name='adcami',
    version=VERSION,
    packages=find_packages(),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author='Sumanth Lingappa',
    author_email='sumanth.lingappa@gmail.com',
    url='https://github.com/sumanth-lingappa/adcami',
    keywords = [
        'citrix adc',
        'aws ami',
        'latest aws citrix adc ami',
    ],
    include_package_date=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIRED,
    entry_points="""
        [console_scripts]
        adcami=adcami.adcami:main
    """,
    python_requires=">=3.6",
)