import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='nameBinaryGenderMap',
      version='1.0.1',
      description='Get the corresponding binary gender class (i.e., male or female) for an input name.',
      long_description=README,
      long_description_content_type="text/markdown",
      url='https://github.com/soheilesm/nameBinaryGenderMap',
      project_urls={
        'Documentation': 'https://github.com/soheilesm/nameBinaryGenderMap/blob/main/README.md',
        'Source': 'https://github.com/soheilesm/nameBinaryGenderMap',
        'Tracker': 'https://github.com/soheilesm/nameBinaryGenderMap/issues',
      },
      author='Soheil Esmaeilzadeh',
      author_email='soes@alumni.stanford.edu',
      license='MIT',
      packages=['nameBinaryGenderMap'],
      include_package_data=True,
      zip_safe=False)