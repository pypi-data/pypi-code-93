from setuptools import setup, find_packages

setup(
    name="pyolive",
    version="0.1.3",
    author="Kiro Lee",
    author_email="kiroly@ingris.com",
    description="A olive worker package",
    url="",
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        "pika >= 1.2.0",
        "dataclasses >= 0.8"
    ],
    python_requires='>=3.6'
)
