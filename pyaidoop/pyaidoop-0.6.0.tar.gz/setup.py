from setuptools import setup, find_packages

long_description = """A python library for AIdoop web-based application platform such as AIdoop-R and AIdoop-P.
Supports camera operation, object trakcing using tensorflow-based deep learning models, opecv-based image processing 
and graphql and websocket to cooperate with web application server"""

INSTALL_REQUIRES = [
    "numpy",
    "opencv-python",
    "opencv-contrib-python",
    "pyrealsense2",
    "requests",
    "gql",
    "websocket-client",
]

setup(
    name="pyaidoop",
    version="0.6.0",
    author="Jinwon Choi",
    author_email="jinwon@ai-doop.com",
    url="https://github.com/aidoop/pyaidoop.git",
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["LICENSE", "README.md", "requirements.txt"],
    },
    license="MIT",
    description="AIdoop web-based platfrom library for robot application platform, AIdoop-R",
    long_description=long_description,
    keywords=[
        "cooperative robot",
        "web-based application",
        "object detection",
        "neural network",
        "CNN",
        "machine learning",
        "computer vision",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
