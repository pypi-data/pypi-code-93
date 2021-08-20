from setuptools import setup

with open("README.md") as fp:
    readme = fp.read()

setup(
    name="sermonaudio",
    version="6.10.3",
    description="The official Python client library for accessing the SermonAudio.com APIs",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
    url="http://api.sermonaudio.com/",
    author="SermonAudio.com",
    author_email="info@sermonaudio.com",
    keywords="sermon audio sermonaudio API preaching church bible",
    license="MIT",
    packages=["sermonaudio", "sermonaudio.node", "sermonaudio.broadcaster"],
    install_requires=["requests>=2.19.1", "pytz>=2018.5", "osis-book-tools>=1.0.1"],
)
