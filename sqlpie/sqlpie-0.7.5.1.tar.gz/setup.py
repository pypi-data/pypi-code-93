import setuptools
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
  long_description = fh.read()

setup_args = dict(
  name='sqlpie',  
  version='0.7.5.1',
  author="Omri Shuva",
  author_email="omrishuva1@gmail.com",
  description="Data lakes Development Framework",
  long_description=long_description,
  long_description_content_type="text/markdown",
  # url="https://github.com/javatechy/dokr",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent"]
)

install_requires = [
    'py-dag',
    'jinja2',
    # 'os',
    # 'glob',
    'PyYAML',
    'pandas'
]

if __name__ == '__main__':
  setup(**setup_args, install_requires=install_requires)