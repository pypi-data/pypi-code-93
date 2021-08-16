from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='AlgorithmLib',
    version='0.0.13',
    packages=setuptools.find_packages(),
    url='https://github.com/pypa/sampleproject',
    license='MIT',
    author=' MA JIANLI',
    author_email='majianli@corp.netease.com',
    description='audio algorithms to compute and test audio quality of speech enhencement',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
    'numpy',
    'wave',
    'matplotlib',
    'datetime',
    'scipy',
    'pystoi',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=[
                ('', ['algorithmLib/p563/p563.dll']),
                ('', ['algorithmLib/POLQA/VQTDll.dll']),
                ('', ['algorithmLib/PEAQ/cygwin1.dll']),
                ('', ['algorithmLib/PEAQ/peaqb.exe']),
                ('', ['algorithmLib/PESQ/PY_PESQ.dll']),
                ],

    python_requires='>=3.8',
)



