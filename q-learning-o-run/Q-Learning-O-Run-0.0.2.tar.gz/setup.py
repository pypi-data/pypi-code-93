import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Q-Learning-O-Run",
    version="0.0.2",
    author="Godw",
    author_email="353055619@qq.com",
    description="用于Q-learning的学习,内含MDP环境和Q-learning决策大脑",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/353055619/Q_Learning_O_Run.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)