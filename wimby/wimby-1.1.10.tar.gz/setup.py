import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name = 'wimby',
    packages = ["wimby"],
    version = '1.1.10',
    license='MIT',
    description = 'Arkivist is a lightweight manager for JSON files.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Rodney Maniego Jr.',
    author_email = 'rod.maniego23@gmail.com',
    url = 'https://github.com/rmaniego/wimby',
    download_url = 'https://github.com/rmaniego/wimby/archive/v1.0.tar.gz',
    keywords = ["cryptocurrency", "analytics", "weighted averages"],
    install_requires=["arkivist", "namari", "shameni", "sometime"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers', 
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3.6'
)