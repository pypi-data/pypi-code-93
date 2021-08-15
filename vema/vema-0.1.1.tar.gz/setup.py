from setuptools import setup

setup(
    name="vema",
    version="0.1.1",
    description="Vema is a solution for developing static web pages, from Python + Flask, which has the basic tools and already configured to focus on the design of the pages.",
    license="MIT",
    author="Epifanio Suárez Martínez",
    author_email="episuarez@pm.es",
    url="https://github.com/episuarez/vema",
    packages=["vema"],
    install_requires=["Flask", "Frozen-Flask", "argparse"],
    scripts=[],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
);