from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setup(
  name='mongomapper',
  description='Mongo ODM for Python',
  long_description=long_description,
  long_description_content_type="text/markdown",
  version='1.1.4',
  license='MIT',
  author='Felipe Cabrera',
  author_email='fecabrera@protonmail.com',
  url='https://github.com/fecabrera/mongomapper',
  project_urls={
    "Bug Tracker": "https://github.com/fecabrera/mongomapper/issues",
  },
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent"
  ],
  packages=find_packages(include=['mongomapper']),
  install_requires=['python-dotenv','pydantic', 'pymongo[srv]'],
  python_requires=">=3.9"
)