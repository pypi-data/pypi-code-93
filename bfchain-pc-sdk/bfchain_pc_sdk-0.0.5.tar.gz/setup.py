import setuptools

with open("README.md", "r", ) as fh:
    long_description = fh.read()

setuptools.setup(
    name="bfchain_pc_sdk",
    version="0.0.5",
    author="Jiang Chao",
    author_email="jiangchao_mars@163.com",
    description="BFchain SDK for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bfcc.dev/",
    # project_urls={
    #     "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    # },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.7',
        # "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "src"},
    packages=['src.bfchain_pc_sdk','src.core','src.util'],
    python_requires=">=2.7, <3",
    install_requires=['requests >= 2.26.0'],
)
