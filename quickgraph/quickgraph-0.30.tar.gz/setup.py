import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name = "quickgraph",
    version = "0.30",
    author = "Mobile Systems and Networking Group, Fudan University",
    author_email = "gongqingyuan@fudan.edu.cn",
    url = "https://gongqingyuan.wordpress.com/",
    description = "A Python package to view the skeleton of a social graph quickly.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
	"Intended Audience :: Science/Research",
	"Topic :: Scientific/Engineering",
    ],
)
