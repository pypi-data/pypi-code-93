from setuptools import setup, find_packages

# setup.py
import os
import sys

version = '1.0.4'

with open("README.md", "r") as fh:
    long_description = fh.read()

if sys.argv[-1] == 'publish':
  if (os.system("python setup.py test") == 0):
          if (os.system("python setup.py sdist upload") == 0):
              if (os.system("python setup.py bdist_wheel upload") == 0):
                 os.system("git tag -a %s -m 'version %s'" % (version, version))
                 os.system("git push")
    
  sys.exit()

# Below this point is the rest of the setup() function

setup(name='SlideRunner_dataAccess',
      version=version,
      description='SlideRunner - data access package (slide access, database access)',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/DeepPathology/SlideRunner_dataAccess',
      author='Marc Aubreville',
      author_email='marc.aubreville@thi.de',
      license='GPL',
      packages=find_packages(),
      package_data={
      }, 
      install_requires=[
          'openslide-python>=1.1.1', 'nibabel>=3.1.1',
          'matplotlib>=2.0.0', 'numpy>=1.13', 'pydicom>=2.1.2', 'pillow>=8.0.1',
      ],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
      ],
      setup_requires=['pytest-runner'],
      entry_points={
        },
      tests_require=['pytest'],
      zip_safe=False)
