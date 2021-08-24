from setuptools import setup, find_packages


def readme():
	with open('./README.md') as f:
		return f.read()


setup(
	name='cyberspace',
	version='2021.8.24.4',
	description='Python library for interacting with IP addresses',
	long_description=readme(),
	long_description_content_type='text/markdown',
	url='https://github.com/idin/cyberspace',
	author='Idin',
	author_email='py@idin.ca',
	license='MIT',
	packages=find_packages(exclude=("jupyter_tests", ".idea", ".git")),
	install_requires=[],
	python_requires='~=3.6',
	zip_safe=False
)
