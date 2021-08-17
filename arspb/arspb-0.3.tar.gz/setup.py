"""Physax setup."""

from setuptools import setup
import os

need_files = []
datadir = "arspb/trained_policies"

setup_py_dir = os.path.dirname(os.path.realpath(__file__))
hh = setup_py_dir + "/" + datadir

for root, dirs, files in os.walk(hh):
  for fn in files:
    ext = os.path.splitext(fn)[1][1:]
    if ext and ext in 'npz txt json '.split(
    ):
      fn = root + "/" + fn
      need_files.append(fn[1 + len(hh):])

print("found resource files: %i" % len(need_files))
for n in need_files:
  print("-- %s" % n)


setup(
    name="arspb",
    version="0.3",
    description="ARS for PyBullet and Tiny Differentiable Simulator (Augmented Random Search, with linear and neural network policy",
    long_description="ARS for PyBullet and Tiny Differentiable Simulator (Augmented Random Search, with linear and neural network policy",
    url="https://github.com/erwincoumans/ARS",
    author="Various",
    author_email="erwincoumans@google.com",
    classifiers=[],
    packages=[
        "arspb","arspb.trained_policies"
    ],
    package_data={'arspb.trained_policies': need_files},
    install_requires=[
        "ray",
        "pybullet",
    ],
)
