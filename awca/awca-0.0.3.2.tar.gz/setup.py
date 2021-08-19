import pathlib
from setuptools import setup, find_packages
import setuptools

install_requires = [
    "poppler-utils",
    "pdf2image",
    "pytesseract",
    "pillow",
    "PyPDF3",
    'torch',
    'transformers==3.1.0',
]

readme_file = pathlib.Path(__file__).parent / "README.md"

short_description = 'A toolkit for making ancient world citation analysis, text summarization, paraphrasing and OCR for PDF to CSV'

setup(
    name='awca',
    version='0.0.3.2',
    description=short_description,
    long_description=readme_file.read_text(),
    long_description_content_type="text/markdown",
    url='https://github.com/UmbraVenus/awca-tools',
    author='Sage Ren (Umbra Venus)',
    author_email='sage.shijie.ren@gmail.com',
    license='MIT', 
    install_requires=install_requires,
    zip_safe=False,
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)