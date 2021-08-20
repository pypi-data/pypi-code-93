from setuptools import setup

with open ("README.md","r") as fh:
    long_description = fh.read()
setup(
    name='emotion_nrc_affect_lex',
    version='0.0.1',
    description='find emotion scores from a list of words',
    py_modules=["emotion"],
    package_dir={'':'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        ],
        long_description = long_description,
        long_description_content_type="text/markdown",
        install_requires = [
            "pandas~=1.1.3",
        ],
        url="https://github.com/tazwar2700/Emotion_NRC_affect_lexicon",
        author = "Syed Mahir Tazwar",
        author_email = "tazwar2700@gmail.com"

)
