from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tracardi-zapier-webhook',
    version='0.1.1',
    description='This plugin calls zapier webhook.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Risto Kowaczewski',
    author_email='risto.kowaczewski@gmail.com',
    packages=['tracardi_zapier_webhook'],
    install_requires=[
        'tracardi_plugin_sdk',
        'pydantic~=1.8.2',
        'asyncio~=3.4.3',
        'aiohttp~=3.7.4.post0'
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
