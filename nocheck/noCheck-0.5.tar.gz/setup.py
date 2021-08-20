from setuptools import setup
with open("README.md",'r') as f:
    long_description = f.read()
setup(name='noCheck',
      version='0.5',
      description="Find highest of two numbers",
      author='Zubair Mushtaq',
      author_email='zubair.mushtaq000@gmail.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=['noCheck'],
      zip_safe=False)
