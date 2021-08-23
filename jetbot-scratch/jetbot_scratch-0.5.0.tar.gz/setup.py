import setuptools
import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="jetbot_scratch",  # Replace with your own username
    version=get_version("jetbot_scratch/__init__.py"),
    author="z14git",
    author_email="lzl1992@gmail.com",
    description="Jetbot 积木编程包",
    url="https://gitee.com/z14git/jetbot_scratch",
    extras_require={
        'all': [],
    },
    install_requires=['simple-pid'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    package_data={
        'jetbot_scratch': ['*.pth']
    }
)
