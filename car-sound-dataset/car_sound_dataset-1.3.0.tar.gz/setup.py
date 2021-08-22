import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="car_sound_dataset",
    version="1.3.0",
    author="Szabolcs Blahut, Matyas Szakalos, Gyorgy Kalmar",
    author_email="nemkonvencionalis@gmail.com",
    description="You can use the car sound dataset with this Python package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blahutszabi/car_sound_dataset",
    project_urls={
        "Bug Tracker": "https://github.com/blahutszabi/car_sound_dataset/issues",
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
                        "setuptools>=42",
                        "wheel",
                        "requests",
                        "googledrivedownloader",
                        "matplotlib",
                        "scipy",
                        "numpy",
                        "sounddevice",
                        "soundfile"
                      ],
)