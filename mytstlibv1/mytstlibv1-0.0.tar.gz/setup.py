import setuptools

with open('requirements.txt') as f:
    REQUIRED = [line for line in f.read().splitlines()]


setuptools.setup(
    name='mytstlibv1',
    version='0.0',
    install_requires=[REQUIRED],
    packages=setuptools.find_packages(),
    include_package_data=True,
    description='',
)
