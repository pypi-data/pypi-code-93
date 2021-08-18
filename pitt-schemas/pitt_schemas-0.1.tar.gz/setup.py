from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pitt_schemas',
      version='0.1',
      description='Pitt JSON Schemas and validators',
      url='https://github.com/ulsdevteam/pitt_schemas',
      author='University of Pittsburgh Library System, Systems Development',
      author_email='uls-systemsdevelopment@pitt.edu',
      long_description=long_description,
      long_description_content_type="text/markdown",
      install_requires=['jsonschema'],
      license='MIT',
      packages=['pitt_schemas'],
      package_dir={'pitt_schemas': 'pitt_schemas'},
      package_data={'pitt_schemas': ['schemas/*.json']},
      test_suite='nose.collector',
      tests_require=['pytest', 'jsonschema'],
      zip_safe=False,
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',)
