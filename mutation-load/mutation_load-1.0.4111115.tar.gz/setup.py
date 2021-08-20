import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name="mutation_load",
        version="1.0.4111115",
        author="Timo_Järvinen",
        author_email="neville160@gmail.com",
        description="VCF permutation tool",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/jarvint12/mutation_load",
        packages=setuptools.find_packages(),
        entry_points = {
            'console_scripts': [
                'mutation-load = mutation_load.mutation_load:main'
            ]
        },
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: BSD License",
            "Operating System :: POSIX :: Linux",
            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Bio-Informatics"
        ],
        include_package_data=True,
        package_data={'': ['mutation_load', 'resources/mutation_load_config.ini', 'r_scripts/mutation_load_coverages_onefile.R', 'r_scripts/mutation_load_coverages_multiple_files.R']},
)

