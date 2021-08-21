import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cdpam", # Replace with your own username
    version="0.0.5",
    author="Pranay Manocha",
    author_email="pranaymnch@gmail.com",
    description="A pip package for an improved perceptual audio metric",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pranaymanocha/PerceptualAudio",
    packages=setuptools.find_packages(),
    package_data={'cdpam': ['CDPAM_trained/scratchJNDdefault_best_model.pth']},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
