from pathlib import Path
from setuptools import setup, find_packages

# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='jsonclasses-flask',
      version='2.5.5',
      description='JSONClasses integration with Flask',
      long_description=README,
      long_description_content_type="text/markdown",
      author='Fillmula Inc.',
      author_email='victor.teo@fillmula.com',
      license='MIT',
      packages=find_packages(exclude=("tests")),
      package_data={'jsonclasses_flask': ['py.typed']},
      zip_safe=False,
      url='https://github.com/fillmula/jsonclasses-flask',
      include_package_data=True,
      python_requires='>=3.9')
