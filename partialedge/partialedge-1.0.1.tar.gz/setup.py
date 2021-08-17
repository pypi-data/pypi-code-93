import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
  name='partialedge',
  packages=setuptools.find_packages(),
  include_package_data=True,
  version='1.0.1',
  license='MIT',
  description='A collection of algorithms for solving Maximum Ink Partial Edge Drawing Problems',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author='Matthias Hummel',
  author_email='matthiashummel@ymail.com',
  url='https://bitbucket.org/Remvipomed/partialedgedrawing/src/master/',
  keywords=['maximum', 'ink', 'partial', 'edge', 'drawing', 'algorithm'],
  install_requires=[
          'networkx>=2',
          'treedecomp>=1',
          'pygeos',
          'matplotlib>=3',
          'scipy>=1'
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Visualization',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
  ],
)
