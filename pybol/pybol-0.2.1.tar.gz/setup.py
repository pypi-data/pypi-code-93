from setuptools import setup, find_packages

version = '0.2.1'

setup(name="pybol",
      version=version,
      description="A library for assembling predefined states of files and directories",
      author="Ian Kenney",
      author_email="ian.kenney@asu.edu",
      packages=find_packages(),
      install_requires = ['pyyaml',
                          'logger',
      ],
      tests_require = ['pytest'],
      zip_safe = True,
)
