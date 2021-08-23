from pathlib import Path

import setuptools

# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# requirements_f = open('requirements.txt', 'r')
# dependencies = [req for req in requirements_f.readlines()]

# This call to setup() does all the work
setuptools.setup(
    name="weedcv",  # how project shows up on website
    version="1.0.4",
    description="Image preprocessing and dataset development tools for weed detection.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/mkutu/weedcv",
    author="WeedCV Team",
    author_email="help@weedcv.com",
    license="MIT",
    classifiers=[
        # How mature is this project? Common values are
        #   2 - Pre-Alpha
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 2 - Pre-Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Image Processing",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
    ],
    # What does your project relate to?
    keywords="dataset development, weed detection, digital agriculture",
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=setuptools.find_packages(),
    # package_dir={"": "weedcv"},
    # packages=setup.find_packages(where="weedcv"),
    install_requires=["numpy", "matplotlib", "opencv-python>4", "scikit-image>0.17.0"],
    test_suite="nose.collector",
    tests_require=["nose"],
)
