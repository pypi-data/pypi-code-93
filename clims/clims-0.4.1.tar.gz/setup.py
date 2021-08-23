from setuptools import setup, find_packages
import sys

python_min_version = (3, 7)
python_requires = '>=' + '.'.join(str(num) for num in python_min_version)


if sys.version_info < python_min_version:
    raise SystemExit('Python 3.7 or later is required!')


with open('README.md') as f:
    long_description = f.read()

setup(
    name="clims",
    description='Command-Line Interface for Materials Simulations',
    author='FHI-aims developers',
    url='https://gitlab.com/FHI-aims-club/utilities/clims',
    packages=find_packages(),
    install_requires = [
        'ase>=3.21.1',
        'spglib>=1.16.1',
        'phonopy>=2.9.3',
        'matplotlib>=3.4.1',
        'click>=7.1.2',
        'pytest>=6.2.3',
    ],
    entry_points={
        'console_scripts': [
            'clims-unit-cell-info=clims.cli.unit_cell_info:unit_cell_info',
            'clims-supercell=clims.cli.supercell:supercell',
            'clims-prepare-run=clims.cli.prepare_run:prepare_run',
            'clims-configure=clims.cli.configure:clims_configure',
            'clims-testsuite=clims.cli.testsuite:testsuite',
            'clims-xyplot=clims.cli.xyplot:xyplot',
            'clims-real2frac=clims.cli.convert_coordinates:real2frac',
            'clims-frac2real=clims.cli.convert_coordinates:frac2real',
            'clims-phonopy-initialize=clims.cli.phonons:clims_initialize_phonopy',
            'clims-phonopy-postprocess=clims.cli.phonons:clims_post_process_phonopy',
            'clims-aimsplot=clims.cli.aimsplot:aimsplot',
            'clims-wigner-seitz-cluster=clims.cli.wigner_seitz_cluster:construct',
            'clims-reinitialize-geometry=clims.cli.reinitialize_geometry:reinitialize_geometry'
        ],
    },
    classifiers=[
        "License :: OSI Approved :: "
        "GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    version='0.4.1',
    license='LGPLv2.1+',
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_data = {'clims.test':['*_default']},
    python_requires = python_requires,
)
