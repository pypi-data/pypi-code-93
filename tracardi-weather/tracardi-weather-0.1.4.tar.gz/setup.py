from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tracardi-weather',
    version='0.1.4',
    description='The purpose of this plugin is to connect to weather server and retrieve weather data in given city.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Risto Kowaczewski',
    author_email='risto.kowaczewski@gmail.com',
    packages=['tracardi_weather'],
    install_requires=[
        'tracardi_plugin_sdk',
        'pydantic',
        'python_weather',
        'tracardi_dot_notation'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    keywords=['tracardi', 'plugin'],
    include_package_data=True,
    python_requires=">=3.8",
)
