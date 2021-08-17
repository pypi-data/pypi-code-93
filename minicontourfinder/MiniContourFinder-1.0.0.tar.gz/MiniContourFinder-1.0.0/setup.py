import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MiniContourFinder",
    version="1.0.0",
    author="Ian S Gilman",
    author_email="ian.gilman@yale.edu",
    description="Lightweight image segmentation software for biological images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wino6687/conda-demo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "cv2",
        "pyperclip",
        "PyQt5",
        "pytesseract",
        "tqdm"
    ]
)