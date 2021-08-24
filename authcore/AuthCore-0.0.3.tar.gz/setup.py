import setuptools
with open("./AuthCore/README.md", "r") as fh:
  long_description = fh.read()
setuptools.setup(
    name='AuthCore',
    version='0.0.3',
    description='AuthCore',
    author='Theta',
    license='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    package_data={
        "": ["*.txt", "*.py", "*.md"]
    },
    zip_safe=False
)

