from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='constellate-client',
    version='0.0.1',
    author='Constellate team',
    author_email='tdm@ithaka.org',
    descripton="Client library for constellate.org",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://constellate.org',
    project_urls={
        "Notebooks": "https://github.com/ithaka/tdm-notebooks",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    license='MIT',
    install_requires=required,
    zip_safe=False,
    include_package_data=True
)
