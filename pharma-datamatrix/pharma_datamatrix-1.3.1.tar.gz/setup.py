from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='pharma_datamatrix',
      version='1.3.1',
      description='Parse EU FMD compliant GS1 & PPN Datamatrix barcodes',
      packages=['pharma_datamatrix'],
      auther = 'Kuldeep Saxena',
      author_email = 'saxenak02@gmail.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/PinchofLogic/pharma_datamatrix",
      zip_safe=False)