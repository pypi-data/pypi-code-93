from setuptools import setup, find_packages

with open('README.md','r') as f:
    long_description = f.read()
VERSION = '0.0.12'
DESCRIPTION = 'Ease working with neural networks'
LONG_DESCRIPTION = 'A package that allows to build simple streams of video, audio and camera data.'

# Setting up
setup(
    name="MiniTensorflow",
    version=VERSION,
    author="Aayushmaan Jain",
    author_email="<aayushmaan1306@gmail.com.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['numpy','pandas'],
    keywords=['python', 'neural', 'network', 'tensorflow', 'keras', 'Machine Learning'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)