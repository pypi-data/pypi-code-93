import setuptools


setuptools.setup(
    name="igi_gc_reader",
    version="0.0.4",
    author="IGI",
    author_email="chris.prosser@igiltd.com",
    description="GC lab file (Excel) -> Excel table formatted sheet.",
    long_description="Create files ready for p:IGI+/Transform import from print formatted GC lab files.",
    long_description_content_type="text/markdown",
    url="https://github.com/IGILtd/data_transformation_scripts/tree/master/import_file_formats/gc",
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: Database",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Text Processing",
        "Typing :: Typed",
    ],
    python_requires='>=3.7',
    packages=setuptools.find_packages(exclude=["tests", "infocompiler"]),
    install_requires=["openpyxl", "xlrd", "tqdm"]
)
