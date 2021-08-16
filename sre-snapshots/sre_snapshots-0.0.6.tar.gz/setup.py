from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='sre_snapshots',
      version='0.0.6',
      description='Download SERP snapshots from the MongoDB library',
      url='',
      author='James Wolman',
      author_email="James.Wolman@found.co.uk",
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='MIT',
      packages=['sre_snapshots'],
      # install_requires=requirements,
      install_requires=[
          "requests==2.25.1",
          "pymongo==3.10.1"
      ],
      include_package_data=True,
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Natural Language :: English",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8"
      ],
      zip_safe=False)
