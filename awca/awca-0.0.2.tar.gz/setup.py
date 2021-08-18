import pathlib
from setuptools import setup, find_packages
import setuptools

install_requires = [
    'torch',
    'transformers==3.1.0',
]

readme_file = pathlib.Path(__file__).parent / "README.md"

short_description = 'A toolkit for making art with machine learning, including an API for popular deep learning models, recipes for combining them, and a suite of educational examples'

setup(
    name='awca',
    version='0.0.2',
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