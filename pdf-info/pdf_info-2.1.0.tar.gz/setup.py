
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(name="pdf_info",
version = "2.1.0",
description="This package extracts important information from a pdf document such as heading, paragraphs and important keywords!!!",
long_description =long_description,
long_description_content_type="text/markdown",
author="Satyam Prakash",
packages=['pdf_info'],
install_requires=["PymuPdf","nltk","pdfminer","sklearn","numpy","PyPDF2"])