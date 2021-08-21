import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="macspoof",
    version="1.1",
    author="Anish M",
    author_email="aneesh25861@gmail.com",
    description="Spoof MAC Address on a Linux PC.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3",
    keywords = ['privacy-tool', 'privacy','student project'],
    url="https://github.com/Anish-M-code/macspoof",
    packages=["macspoof"],
    classifiers=(
        'Development Status :: 5 - Production/Stable',      
        'Intended Audience :: Developers',      
        'Topic :: Software Development',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',   
        'Programming Language :: Python :: 3',      
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
    ),
    entry_points={"console_scripts": ["macspoof = macspoof:main",],},
)
