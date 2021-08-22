import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="k8kat",
  version="0.0.244",
  author="NMachine",
  author_email="xavier@nmachine.io",
  description="Sugar for Kubernetes",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/nmachine-cs/k8kat",
  packages=setuptools.find_packages(exclude=[
    "k8kat.tests.*", "k8kat.tests"
  ]),
  install_requires=[
    "python-dotenv",
    "kubernetes",
    "typing-extensions",
    "inflection"
  ],
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires='>=3.6'
)
