import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="chaos-cases",
  version="0.0.1",
  author="haohaiyo",
  author_email="admin@b7.com",
  description="生成一些通用的测试用例",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/haoheiyo/chaos-cases",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)
