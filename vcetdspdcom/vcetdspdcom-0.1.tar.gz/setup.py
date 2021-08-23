import setuptools
classifiers=[
        "Development Status :: 2 - Pre-Alpha",
		"Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
		"Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering"
    ]
setuptools.setup(
    name="vcetdspdcom", # Replace with your own username
    version="0.1",
    author="Shivaprasad Rao",
    author_email="shivarao101@gmail.com",
    description="Basic Signal Processing algorithms and Communication Modulation techniques Package",
    long_description=open('README.txt').read()+'\n\n'+ open('CHANGELOG.txt').read(),
    long_description_content_type="text/markdown",
    url="https://www.linkedin.com/in/shivaprasad-rao-a92b8219/",
	classifiers=classifiers,
	keywords="DSP DCOM",
    packages=setuptools.find_packages(),
	install_requires=['numpy'],
    python_requires='>=3.6',
)
