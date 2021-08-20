import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
  name='MathProCore',
  version="0.0.1",
  author='Nima Rahmanian',
  author_email='nimarahmanian8@gmail.com',
  description='Use MathPro to generate unlimited math practice problems from question templates!',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url='https://github.com/Nimsi123/MathProgram', # update
  classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
  ],
  install_requires=[
      "sympy >= 1.8",
      "numpy >= 1.21.1"
  ],
  python_requires=">=3.6",
  packages=setuptools.find_packages(where="src"),
  package_dir={"": "src"},    
)