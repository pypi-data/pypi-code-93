from setuptools import setup,find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='wikikoro',
      version='0.1',
      description='Find In wikipedia',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/AshfakYeafi/wikiit',
      author='Ashfak Yeafi',
      author_email='yeafiashfak@gmail.com',
      license='MIT',
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
                        ],
      package_dir={"": "src"},
      packages=find_packages(where="src"),
      install_requires=[
          'wikipedia',
      ],
      include_package_data=True,
      zip_safe=False)
