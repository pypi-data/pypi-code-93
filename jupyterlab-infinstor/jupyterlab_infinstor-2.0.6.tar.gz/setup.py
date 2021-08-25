"""
Setup module for the jupyterlab_infinstor proxy extension
"""
import setuptools

from setupbase import create_cmdclass
from setupbase import ensure_python
from setupbase import find_packages

data_files_spec = [
    (
        "etc/jupyter/jupyter_notebook_config.d",
        "configs",
        "jupyterlab_infinstor.json",
    ),
]

cmdclass = create_cmdclass(data_files_spec=data_files_spec)

setup_dict = dict(
    name="jupyterlab_infinstor",
    description="InfinStor Jupyter Server extension",
    packages=find_packages(),
    cmdclass=cmdclass,
    author="InfinStor, Inc.",
    author_email="support@infinstor.com",
    license="AGPL-3.0",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "JupyterLab", "InfinStor", "InfinSnap", "InfinSlice"],
    python_requires=">=3.5",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    install_requires=["notebook", "boto3", "jupyterlab>=2", "aiohttp", "jsons"],
)

try:
    ensure_python(setup_dict["python_requires"].split(","))
except ValueError as e:
    raise ValueError(
        "{:s}, to use {} you must use python {} ".format(
            e, setup_dict["name"], setup_dict["python_requires"]
        )
    )

setuptools.setup(version="2.0.6", **setup_dict)
