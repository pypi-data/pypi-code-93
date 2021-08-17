import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent
__version__ = "1.0.2"
# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setuptools.setup(
    name="file_operations",
    version=__version__,
    description="Simple API for performing file and directory operations",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Algorithms Path",
    author_email="support@algorithmspath.com",
    url='http://pypi.python.org/pypi/file_operations/',
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    # packages=setuptools.find_packages(),
    # package_data={'example' : ['kmp_utils/example.cpython-38-x86_64-linux-gnu.so']},
    include_package_data=True,
    install_requires=[],
    python_requires='>=3'
)

# python3 setup.py sdist bdist_wheel
# twine upload dist/*
