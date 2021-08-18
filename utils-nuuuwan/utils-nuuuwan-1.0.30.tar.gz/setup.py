"""Setup."""

import setuptools

DIST_NAME = 'utils'
version = "1.0.30"

setuptools.setup(
    name="%s-nuuuwan" % DIST_NAME,
    version=version,
    author="Nuwan I. Senaratna",
    author_email="nuuuwan@gmail.com",
    description="Simple extensions to the core python libraries.",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/nuuuwan/%s" % DIST_NAME,
    project_urls={
        "Bug Tracker": "https://github.com/nuuuwan/%s/issues" % DIST_NAME,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        'area',
        'bs4',
        'psutil',
        'requests',
        'selenium',
        'tweepy',
        'pandas',
        'shapely',
        'geopandas',
        'pillow',
        'matplotlib',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
