from setuptools import setup
from setuptools.extension import Extension

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kingcow",
    version='1.0.1', 
    author='Zhou_Chengyu', 
    author_email='earuil@outlook.com', 
    description='This is a library for web page parsing and web page requests',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Zhou-chengy/kingcow/',
    packages=['kingcow'],
)
