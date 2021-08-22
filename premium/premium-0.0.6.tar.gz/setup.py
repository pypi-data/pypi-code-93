import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="premium",
    version="0.0.6",
    author="slipper",
    author_email="byteleap@gmail.com",
    description="Python AI toolkits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GaoangLiu/psox",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        # And include any *.msg files found in the "hello" package, too:
        "premium": ['localdata/*.txt', 'localdata/*.pickle', 'localdata/*.mp3', 'localdata/*.wav'],
    },
    install_requires=['smart-open', 'optuna'],
    entry_points={
        'console_scripts': ['demo=premium.demo:entry', 'zz=premium.zz:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
