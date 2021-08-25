"""Setup for the cross_framework_hpo package."""

import setuptools


setuptools.setup(
    author="Max Zvyagin",
    author_email="max.zvyagin7@gmail.com",
    name='cross_framework_hpo',
    license="MIT",
    description='Hyperparameter Search tools in order to quantify differences between deep learning frameworks',
    version='v0.0.1',
    long_description='https://github.com/maxzvyagin/cross_framework_hpo',
    url='https://github.com/maxzvyagin/cross_framework_hpo',
    packages=setuptools.find_packages(),
    python_requires=">=3.5",
    install_requires=['spaceray', 'torch', 'pytorch_lightning', "tensorflow", "wandb"],
    classifiers=[
        # Trove classifiers
        # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
)