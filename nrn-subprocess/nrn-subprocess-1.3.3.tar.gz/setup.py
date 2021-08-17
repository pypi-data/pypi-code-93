import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nrn-subprocess",
    author="Robin De Schepper",
    version="1.3.3",
    packages=["nrnsub"],
    description="Run isolated NEURON simulations in a single Python session.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["dill", "tblib"]
)
