try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="preserves",
    version="0.7.0-rc1",
    author="Tony Garnock-Jones",
    author_email="tonyg@leastfixedpoint.com",
    license="Apache Software License",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
    packages=["preserves"],
    url="https://gitlab.com/preserves/preserves",
    description="Experimental data serialization format",
    install_requires=[],
    python_requires=">=3.6, <4",
)
