from setuptools import setup,find_packages

with open("README.md",'r') as fh:
    long_description = fh.read()

setup(
    name="cuhk_seis",
    author="Hardy ZI",
    version="0.0.2",
    author_email='zijinping@hotmail.com',
    description = 'package for earthquake location purpose',
    long_description = long_description,
    license = "MIT",
    packages = find_packages(),
    install_requires=[
    'EQTransformer>=0.1.59',
    'obspy',
    'tqdm==4.48.0',
    'jupyter',
    'scipy==1.4.1',
    'numpy>=1.21.0'],
    python_requires = ">=3.7",
    setup_requires=['numpy>=1.21.0']
)
