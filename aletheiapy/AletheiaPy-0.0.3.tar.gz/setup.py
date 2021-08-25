from setuptools import setup

with open("README.md", "r") as fh:
	long_description = fh.read()

setup(
	name = 'AletheiaPy',
	version = '0.0.3',
	description = 'AletheiaPy is a Python wrapper of Aletheia API, which provides access to financial data.',
	py_modules = ["Aletheia"],
	package_dir = {'':'src'},
	classifiers=["Programming Language :: Python :: 3.7","License :: OSI Approved :: MIT License","Operating System :: OS Independent"],
	long_description=long_description,
	long_description_content_type="text/markdown",
	install_requires=["requests"], # extras_require = {"dev":["pytest>=3.7"]},
	url="https://github.com/lliang17/AletheiaPy",
	author="Lyndon Liang",
	author_email="lyndon.y.liang@gmail.com"
)