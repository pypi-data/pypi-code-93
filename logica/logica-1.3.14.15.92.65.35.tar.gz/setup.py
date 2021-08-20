import setuptools

with open("logica/README.md", "r") as f:
  long_description = f.read()

setuptools.setup(
  name = "logica",
  version = "1.3.14.15.92.65.35",
  author = "Evgeny Skvortsov",
  author_email = "logica@evgeny.ninja",
  description = "Logica language.",
  long_description = long_description,
  long_description_content_type = "text/markdown",
  url="https://github.com/evgskv/logica",
  packages=setuptools.find_namespace_packages(),
  classifiers = [
      "Topic :: Database",
      "License :: OSI Approved :: Apache Software License"
  ],
  entry_points = {
    'console_scripts': ['logica=logica.logica:run_main']
  },
  python_requires= ">=3.0"
)

