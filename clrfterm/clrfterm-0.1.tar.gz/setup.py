from setuptools import setup

with open("readme.md") as f:
    description = f.read()

setup(name='clrfterm',
      version='0.1',
      description="Module that decorates your console",
      packages=['clrfterm'],
      long_description=description,
      long_description_content_type='text/markdown',
      zip_safe=False
)


