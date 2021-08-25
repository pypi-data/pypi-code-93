import setuptools
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.read().split("\n")

setuptools.setup(
    name="bodo_platform_extensions",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Sahil Gupta",
    author_email="",
    description="Jupyter Notebook/Lab extensions for the Bodo Cloud Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bodo-inc/bodo-platform-extensions",
    packages=setuptools.find_packages(),
    # include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
