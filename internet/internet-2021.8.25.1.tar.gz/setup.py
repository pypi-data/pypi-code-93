from setuptools import setup, find_packages


def readme():
	with open('./README.md') as f:
		return f.read()


setup(
	name='internet',
	version='2021.8.25.1',
	description='Python library for working with IP addresses and other internet related functionalities',
	long_description=readme(),
	long_description_content_type='text/markdown',
	url='https://github.com/idin/internet',
	author='Idin',
	author_email='py@idin.ca',
	license='MIT',
	packages=find_packages(exclude=("jupyter_tests", ".idea", ".git")),
	install_requires=['base32hex', 'numpy', 'pandas', 'pyspark', 'disk'],
	python_requires='~=3.6',
	zip_safe=False
)

# todo add ipv6 to the library
