import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="FicusFramework",
    version="3.0.12.post1",

    packages=find_packages('src'),
    package_dir={'': 'src'},
    test_suite="test",

    install_requires=["flask>=1.1.2", "flask-cors>=3.0.8", "requests>=2.23.0", "apscheduler>=3.6.3", "jsonpath-rw>=1.4.0",
                      "munch>=2.5.0", "PyYaml>=5.3.1", "readerwriterlock>=1.0.7", "confluent-kafka>=1.3.0",
                      "sqlalchemy>=1.3.3", "mysqlclient","pymongo","gevent","Celery==4.4.7","redis>=3.5.3","python-consul2"],

    author='sunxiang0918',
    author_email="sunxiang0918@gmail.com",
    description="A framework for Ficus by Python3.",
    long_description=read("README.rst"),
    license="MIT",
    keywords="ficus framework python",
    url="https://git.sobey.com/SobeyHive/FicusFramework4Py",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Natural Language :: Chinese (Simplified)",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    zip_safe=False
)
