import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="niota",
    version="0.6.2",
    author="Numbers Co., Inc",
    author_email="hi@numbersprotocol.io",
    description="Numbers PyOTA Wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/numbersprotocol/niota",
    packages=setuptools.find_packages(),
    license='GPLv3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "cryptography>=3.4.6",
        "ipfshttpclient>=0.6.0",
        "PyOTA>=2.1.0",
        "pycryptodome>=3.10.1",
        "python-magic>=0.4.18",
    ],
    python_requires=">=3.6",
)
