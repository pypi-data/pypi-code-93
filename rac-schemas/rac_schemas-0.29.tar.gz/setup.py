from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='rac_schemas',
      version='0.29',
      description='RAC JSON Schemas and validators',
      url='http://github.com/RockefellerArchiveCenter/rac_schemas',
      author='Rockefeller Archive Center',
      author_email='archive@rockarch.org',
      long_description=long_description,
      long_description_content_type="text/markdown",
      install_requires=['jsonschema'],
      license='MIT',
      packages=['rac_schemas'],
      package_dir={'rac_schemas': 'rac_schemas'},
      package_data={'rac_schemas': ['schemas/*.json']},
      test_suite='nose.collector',
      tests_require=['pytest', 'jsonschema'],
      zip_safe=False,
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.6',)
