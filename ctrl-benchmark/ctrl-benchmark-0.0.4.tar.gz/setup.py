# Copyright (c) Facebook, Inc. and its affiliates.
# 
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ctrl-benchmark",
    version="0.0.4",
    author="Tom Veniat, Ludovic Denoyer & Marc'Aurelio Ranzato",
    author_email="veniat.tom@pm.me",
    url="https://github.com/facebookresearch/CTrLBenchmark",
    license="MIT License",
    description="The Continual Transfer Learning Benchmark",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        'pyyaml',
        'torch>=1.3,<2',
        'torchvision<1',
        'networkx>2,<3',
        'plotly',
        'pydot',
        'tqdm',
        'scikit-learn',
        'bs4'
    ],
    include_package_data=True,
)