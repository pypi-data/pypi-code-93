import setuptools


from cmdtools import __version__ as version


setuptools.setup(
    name="cmdtools-py",
    description="command text parser and command processor",
    version=version,
    author="HugeBrain16",
    author_email="joshtuck373@gmail.com",
    license="MIT",
    keywords="command-parser command-processor command cmd cmd-parser",
    url="https://github.com/HugeBrain16/cmdtools",
    packages=["cmdtools", "cmdtools/ext"],
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
    ],
)
