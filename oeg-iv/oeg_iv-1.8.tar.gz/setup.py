"""For pypi.org upload."""
import setuptools

LONG = """
# oeg.iv

Python package for communication with InspectionViewer app
"""

setuptools.setup(
  name='oeg_iv',
  version='1.8',
  author='Vitaly Bogomolov',
  author_email='mail@vitaly-bogomolov.ru',
  description='Python package for communication with InspectionViewer app',
  long_description=LONG,
  long_description_content_type="text/markdown",
  url='https://github.com/vb64/oeg.iv',
  packages=['oeg_iv', 'oeg_iv.csvfile'],
  download_url='https://github.com/vb64/oeg.iv/archive/v1.8.tar.gz',
  keywords=['python', 'InspectionViewer', 'csv'],
  classifiers=[
    "Programming Language :: Python",
    # https://autopilot-docs.readthedocs.io/en/latest/license_list.html
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
  ],
)
