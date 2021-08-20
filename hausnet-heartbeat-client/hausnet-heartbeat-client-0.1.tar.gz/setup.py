""" Create a package. Steps:
      1. Update the version number in this file.
      2. Create source distribution:
         python setup.py sdist
      3. Upload to test pypi (replace VERSION with the latest version number):
         twine upload --repository-url https://test.pypi.org/legacy/ dist/hausnet-heartbeat-client-[VERSION].tar.gz
      4. Test installing package:
         pip install --index-url https://test.pypi.org/simple/ hausnet-heartbeat-client --user
      4. Upload to pypi (replace VERSION with the latest version number)
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hausnet-heartbeat-client",
    version="0.1",
    author="HausNet Developers",
    author_email="dev@hausnet.io",
    description="A client for the Heartbeat monitoring service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HausNet/heartbeat-client",
    packages=setuptools.find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=['bravado']
)
