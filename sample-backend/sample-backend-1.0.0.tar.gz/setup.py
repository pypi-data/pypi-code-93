from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh1:
    long_description = fh1.read()

#with open("CHANGELOG.txt", "r", encoding="utf-8") as fh2:
#    change_log = fh2.read()

VERSION = '1.0.0'

setup(name='sample-backend',
    version=VERSION,
    description='Sample backend for todo-list application',
    long_description=long_description,
    long_description_content_type="text/markdown",
    #change_log = change_log,
    url='https://github.com/malonejv/py-sample-backend',  
    project_urls={
        "Bug Tracker": "https://github.com/malonejv/py-sample-backend/issues",
    },
    author='Javier López Malone',
    author_email='malonejv@gmail.com',
    license='MIT', 
    keywords=['todolist','todo'], 
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
)
