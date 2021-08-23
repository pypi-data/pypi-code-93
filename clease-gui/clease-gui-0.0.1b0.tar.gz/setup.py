from setuptools import setup, find_packages

# Get version number
about = {}
with open('clease_gui/version.py') as f:
    exec(f.read(), about)
version = about['__version__']

EXTRAS_REQUIRE = {
    'dev': (
        'pre-commit',
        'yapf',
        'prospector',
        'pylint',
        'twine',
    ),
    'test': (
        'pytest>=4',
        'pytest-mock',
        'pytest-cases',
    ),
    'doc': ('sphinx', 'sphinx_rtd_theme'),
}

EXTRAS_REQUIRE['full'] = set(value for tup in EXTRAS_REQUIRE.values()
                             for value in tup)

setup(
    name="clease-gui",
    author='Alexander S. Tygesen',
    author_email="alexty@dtu.dk",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitlab.com/computationalmaterials/clease-gui',
    version=version,
    description="CLuster Expansion in Atomistic Simulation Environment GUI",
    packages=find_packages(include=['clease_gui', 'clease_gui.*']),
    license='MPL-2.0',
    keywords=[
        'Cluster Expansion',
        'Monte Carlo',
        'Computational materials',
        'Materials research',
        'GUI',
        'Graphical User Interface',
    ],
    project_urls={
        'Documentation': 'https://clease-gui.readthedocs.io/',
        'Source': 'https://gitlab.com/computationalmaterials/clease-gui',
    },
    python_requires=">=3.7",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    install_requires=[
        'ipython',
        'jupyter',
        # Set to master branch for now, since we need some things from there.
        # 'clease @ git+https://gitlab.com//computationalmaterials/clease.git@master',
        'clease>=0.10.4',
        'pandas',
        'numpy',
        'matplotlib',
        'ase',
    ],
    extras_require=EXTRAS_REQUIRE,
    include_package_data=True,  # Include stuff in MANIFEST.in
)
