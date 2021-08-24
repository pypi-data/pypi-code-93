import setuptools
from importlib.util import module_from_spec, spec_from_file_location

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


spec = spec_from_file_location("constants", "./src/canalyst_candas/version.py")
constants = module_from_spec(spec)
spec.loader.exec_module(constants)

__version__ = constants.__version__


setuptools.setup(
    name="canalyst_candas",
    version=__version__,
    author="Canalyst",
    author_email="support+api@canalyst.com",
    description="The official Canalyst Software Development Kit (SDK) for our public API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={"Bug Tracker": "https://github.com/pypa/sampleproject/issues"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)
