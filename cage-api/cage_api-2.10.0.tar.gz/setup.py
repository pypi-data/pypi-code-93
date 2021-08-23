import setuptools

with open("README.md.pypi", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    # https://stackoverflow.com/questions/58533084/what-keyword-arguments-does-setuptools-setup-accept
    name="cage_api",
    version="2.10.0",
    description="Cage system API for remote file access",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Arselon/Cage",
    author="Arslan Aliev",
    author_email="arslanaliev@yahoo.com",
    maintainer="Arslan Aliev",
    maintainer_email="arslanaliev@yahoo.com",	
    license="Apache",
    packages=setuptools.find_packages(), 	
    keywords= [
		'Cage', 
		'remote file access'
	],
	python_requires=">=3.7",	
    classifiers=[
        "Programming Language :: Python :: 3.7",
	    "Intended Audience :: Developers",	
    ],
)