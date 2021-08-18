from setuptools import find_packages, setup
import pathlib

HERE = pathlib.Path(__file__).parent

README = ( HERE / "README.md").read_text() 
setup(
    name='AutoFeedback',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
        'numpy',
        'scipy',
        'sympy'],
    version='0.1.12',
    description='check basic python exercises with pretty feedback',
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/abrown41/AutoFeedback",
    author='Andrew Brown',
    author_email="andrew.brown@qub.ac.uk",
    license='MIT',
)
