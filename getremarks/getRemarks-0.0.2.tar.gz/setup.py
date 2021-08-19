from setuptools import setup
with open("README.md",'r') as f:
    long_description = f.read()
setup(name='getRemarks',
      version='0.0.2',
      description="Find grade scored and then remarks regarding the grade",
      author='Seyed Muzaffar',
      author_email='iammseyed@protonmail.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=['getRemarks'],
      zip_safe=False)
