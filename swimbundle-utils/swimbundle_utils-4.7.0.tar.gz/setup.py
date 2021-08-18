from setuptools import setup
import json


def parse_requirements(requirement_file):
    with open(requirement_file) as f:
        return f.readlines()


def version_info():
    with open("version.json", "r") as f:
        return json.load(f)


with open('./README.rst') as f:
    long_description = f.read()

v_info = version_info()

setup(
    name='swimbundle_utils',
    packages=['swimbundle_utils'],
    version=v_info["version"],
    description='Swimlane Bundle Utilities Package',
    author=v_info["author"],
    author_email="info@swimlane.com",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=parse_requirements('./requirements.txt'),
    keywords=['utilities', 'dictionary', 'rest'],
    classifiers=[
        "Programming Language :: Python :: 3"],
    include_package_data=True
)
