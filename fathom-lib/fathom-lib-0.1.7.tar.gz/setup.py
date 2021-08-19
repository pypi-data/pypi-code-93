from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fathom-lib", 
    version="0.1.7",
    description="Fathom lib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fathom-io/fathom-lib",
    project_urls={
        "Bug Tracker": "https://github.com/fathom-io/fathom-lib/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "cycler==0.10.0",
        "decorator==4.4.2",
        "joblib==0.15.1",
        "kiwisolver==1.2.0",
        "matplotlib==3.2.2",
        "networkx==2.4",
        "numpy==1.18.5",
        "pandas==1.0.4",
        "pyparsing==2.4.7",
        "python-dateutil==2.8.1",
        "pytz==2020.1",
        "scikit-learn==0.23.1",
        "scipy==1.4.1",
        "six==1.15.0",
        "threadpoolctl==2.1.0",
        "dataclasses-json==0.5.1",
        "rethinkdb==2.4.7",
        "pytest==5.4.3",
        "xgboost==1.1.1",
        "lifelines==0.25.2",
        "shap==0.35.0",
        "Pillow==7.2.0",
        "fire==0.3.1",
        "pyod==0.8.0",
        "mlflow",
        "simplejson",
        "keras-tuner",
        "autokeras",
        "holoviews==1.13.5",
        "lightgbm==3.0.0",
        "channels==3.0.3",
        "plotly==4.14.3",
        "jinja2==2.11.3"
    ],
    dependency_links=[
        "https://storage.googleapis.com/logicai-fathom/python-wheels/mlflow-1.10.1.dev0-py3-none-any.whl",
        "git+https://github.com/keras-team/keras-tuner.git@1.0.2",
        "git+https://github.com/keras-team/autokeras.git@master"
    ],
    packages=find_packages(),
    python_requires=">=3.6",
)