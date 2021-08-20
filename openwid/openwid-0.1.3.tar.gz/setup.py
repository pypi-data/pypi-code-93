from setuptools import setup

with open("README.md", "r") as fh:
      long_description = fh.read()

setup(
      name='openwid',
      version='0.1.3',
      url="https://github.com/tolgahancepel/openwid",
      author="Tolgahan Cepel",
      author_email="tolgahan.cepel@gmail.com",
      description='OpenWeather in Dash',
      long_description = long_description,
      long_description_content_type="text/markdown",
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Framework :: Dash",
      ],
      packages=['openwid'],
      zip_safe=False
)