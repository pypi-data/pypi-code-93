import setuptools
import pkg_resources

pkg_resources.require("setuptools>=57.0.0")
setuptools.setup(
    packages=setuptools.find_packages(),
)
