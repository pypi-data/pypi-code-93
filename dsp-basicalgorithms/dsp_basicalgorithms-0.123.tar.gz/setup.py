import setuptools

setuptools.setup(
    name="dsp_basicalgorithms", # Replace with your own username
    version="0.123",
    author="Shivaprasad Rao",
    author_email="shivarao101@gmail.com",
    description="Basic Dsp algorithms and Filter Design",
    long_description=open('README.txt').read()+'\n\n'+ open('CHANGELOG.txt').read(),
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
