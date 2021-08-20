from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="django-createsuperuser-signal",
    version="0.0.1",
    description="Django app to create superuser from environment after migrations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Babis Kaidos",
    author_email="ckaidos@intracom-telecom.com",
    url="https://github.com/BabisK/django-createsuperuser",
    packages=find_packages(),
    install_requires=[
        "Django>=1.8"
    ],
    license="Apache Software License",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django :: 1.8",
        "Framework :: Django :: 1.9",
        "Framework :: Django :: 1.10",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Site Management"
    ]
)
