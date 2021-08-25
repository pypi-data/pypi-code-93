"""
Created on Aug 20, 2021

@author: Euncheon Lim @ Chosun University

"""
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    
with open("README.md", "r") as fh:
    long_description = fh.read()
    
install_reqs = [
    "tensorflow==2.2.0",
    "scipy==1.4.1",
    "pandas>=1.2.3",
    "numpy>=1.19.2",
    "keras>=2.4.3",
    "nibabel>=3.2.1",
    "joblib>=1.0.1",
    "tqdm>=4.59.0",
    ]

print(find_packages(where="./src"))

setup(
    name="deepparcellation",
    version="1.0.6",
    url="https://github.com/abysslover/deepparcellation",
    author="Eun-Cheon Lim",
    author_email="abysslover@gmail.com",
    license="GPL3.0",
    description="DeepParcellation: fast and accurate fast and accurate brain MRI parcellation by deep learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": ".", "deepparcellation": "./src/deepparcellation"},
    packages=find_packages(where="./src"),
    package_data={"deepparcellation": ["*.txt", "*.json"], "deepparcellation.weights": ["*.h5"]},
    install_requires=install_reqs,
    include_package_data=True,
    python_requires=">=3.8",
    entry_points = {
        "console_scripts": ["deepparcellation=deepparcellation.entry:main"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Programming Language :: Python :: 3",
    ],
    keywords="brain MRI parcellation tensorflow keras",
)