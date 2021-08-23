import setuptools

# python setup.py sdist bdist_wheel
# twine upload dist/*

with open("README.md", "r", encoding="utf8") as fh:
	long_description = fh.read()

setuptools.setup(
	name="sigmatmpy",
	version="0.0.24",
	author="SigmaTM",
	author_email="wuyou1020@hotmail.com",
	description="SigmaTM manager api for python user",
	install_requires=[
        'pandas',
        'websocket-client'
    ],
	long_description=long_description,
	long_description_content_type="text/markdown",
	packages=setuptools.find_packages(),
	classifiers=[
	"Programming Language :: Python :: 3",
	"License :: OSI Approved :: MIT License",
	"Operating System :: OS Independent",
	],
)