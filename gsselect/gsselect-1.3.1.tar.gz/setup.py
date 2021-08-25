import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='gsselect',
    version='1.3.1',
    author="Bryan Miller",
    author_email="millerwbryan@gmail.com",
    description="Gemini guide star selection and URL target-of-opportunity (TOO) triggering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bryanmiller/gsselect",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'astropy',
        'matplotlib',
        'numpy>=1.15.4',
        're'
        'requests'
    ]
)