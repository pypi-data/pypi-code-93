import setuptools
from distutils.command.build_py import build_py
import os
import json

class BuildConfiguresScriptDir(build_py):
    def run(self):
        build_py.run(self)
        if self.dry_run:
            return

        current_dir = os.path.realpath(__file__)
        package_path = current_dir.split('/')[:-1]
        package_path = "/".join(package_path)
        dist_dir = f"{os.path.dirname(os.path.abspath(__file__))}/multiSourceWordMaps"
        config_path = f"{dist_dir}/config.py"
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        config["package_dir"] = f"{package_path}"
        with open(config_path, "w+") as config_file:
            config_file.write(json.dumps(config))
        

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.readlines()

setuptools.setup(
    name="multiSourceWordMaps",
    version="0.0.7",
    author="Ot Gabaldon Torrents",
    author_email="gabaldonot@gmail.com",
    description="Allows the user to list sources and compile word maps from those sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.thisiswhy.biz",
    project_urls={
        "Bug Tracker": "https://www.thisiswhy.biz",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires = requirements,
    entry_points= {
        'console_scripts': [
            'map = multiSourceWordMaps.wordMapCreator:main'
        ]
    },
    cmdclass= {
        'build_py': BuildConfiguresScriptDir,
    }
)