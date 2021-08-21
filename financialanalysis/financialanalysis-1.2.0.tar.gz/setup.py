# Aug 15, 2021

from setuptools import setup, find_packages
import io
from os import path
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    # print(long_description)
setup(
    name='financialanalysis',
    version="1.2.0",
    author='Yoshio Yamauchi == SPARKLE',
    author_email='sparkle.official.01@gmail.com',
    long_description_content_type="text/markdown",
    description="All-in-one tools for financial analysis",
    long_description=long_description,
    url="https://github.com/YoshioYamauchi/financialanalysis",
    license='MIT',
    platforms=['any'],
    # install_requires=["stem==1.8.0", "random-user-agent==1.0.1", "numpy==1.19.4",
    #                   "requests_html==0.10.0", "lxml==4.6.2", "requests==2.25.1", "bs4==0.0.1",
    #                   "pandas", "urllib3==1.26.2", "sklearn"],
    install_requires=["numpy",
                      "pandas", "sklearn"],
    keywords='pandas, finance, pandas datareader',
    packages=find_packages(include=["financialanalysis", "financialanalysis.*"]),
    python_requires=">=3.6",
    # install_requires=["stem>="]
    entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },
)

print("installation finished!")
# python3 setup.py sdist
# twine upload dist/*
