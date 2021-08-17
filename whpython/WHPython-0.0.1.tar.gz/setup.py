import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

config = {}
with open('config.py', 'r', encoding='utf-8') as f:
  exec(f.read(), config)

setuptools.setup(
  name = config["name"],
  version = config["version"],
  author = config["author"],
  author_email = config["author_email"],
  description = config["description"],
  long_description = long_description,
  long_description_content_type = "text/markdown",
  url = "https://github.com/pypa/sampleproject",
  packages = setuptools.find_packages(),
  classifiers = [
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)