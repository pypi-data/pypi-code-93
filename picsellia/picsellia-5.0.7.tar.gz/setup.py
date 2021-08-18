import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="picsellia", # Replace with your own username
    version="5.0.7",
    author="Pierre-Nicolas Tiffreau CTO @ Picsell.ia",
    author_email="pierre-nicolas@picsellia.com",
    description="Python SDK raining module for Picsell.ia",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://www.picsellia.com',
    keywords=['SDK', 'Picsell.ia', 'Computer Vision', 'Deep Learning'],
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy>=1.18.5",
        "Pillow>=7.2.0",
        "requests>=2.24.0",
        "scipy>=1.4.1",
        "beartype>=0.7.1"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    python_requires='>=3.6.9',
)