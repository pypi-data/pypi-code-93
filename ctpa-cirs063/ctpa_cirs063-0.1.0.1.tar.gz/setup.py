

from setuptools import setup, find_packages
README = 'README.md'

DESCRIPTION = 'Phantom analysis toolkit to fully automatically analyse several CT phantoms'
NAME = 'ctpa_cirs063'

VERSION = "0.1.0.1"


def readme():
    with open(README) as f:
        return f.read()


setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Intended Audience :: Science/Research',
        'Natural Language :: English'
      ],
      keywords='image images medical dicom CT phantom',
      url='',
      author='Niels van der Werf',
      author_email='n.vanderwerf@erasmusmc.nl',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'pydicom',
          'scipy',
          'numpy',
      ],
      include_package_data=True,
      zip_safe=False)