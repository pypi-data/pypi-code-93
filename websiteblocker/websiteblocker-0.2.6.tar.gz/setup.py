import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="websiteblocker",
    version="0.2.6",
    author="Anish M",
    author_email="aneesh25861@gmail.com",
    description="Blocks distracting websites in Windows , Mac OS and Linux Based Distros .",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3+",
    keywords = ['Website Blocker', 'hosts file','student project'],
    url="https://github.com/Anish-M-code/Simple_Website_blocker",
    packages=["websiteblocker"],
    classifiers=(
        'Development Status :: 5 - Production/Stable',      
        'Intended Audience :: Developers',      
        'Topic :: Software Development',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',   
        'Programming Language :: Python :: 3',      
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
  
    ),
    entry_points={"console_scripts": ["websiteblocker = websiteblocker:main",],},
)
