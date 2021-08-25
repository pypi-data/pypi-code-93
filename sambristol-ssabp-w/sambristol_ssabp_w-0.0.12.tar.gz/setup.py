import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sambristol_ssabp_w",
    version="0.0.12",
    author="Sam Cameron",
    author_email="samuel.j.m.cameron@gmail.com",
    description="package to compute ODE's and statmech "
    "relevant to active brownian particle steady states",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/samueljmcameron/sambristol_ssabp_w",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License "
        "v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.3',
    install_requires=['scipy','numpy','samspecialfuncs>=0.0.15']
)
