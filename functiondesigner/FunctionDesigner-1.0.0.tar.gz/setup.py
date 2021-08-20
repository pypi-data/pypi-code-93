import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="FunctionDesigner",
  version="1.0.0",
  author="zjy_090820",
  author_email="a1234567890001919@outlook.com",
  description="to establish yourselfs function",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)
