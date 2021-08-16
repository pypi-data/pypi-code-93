import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()
# with open('requirements.txt') as f:
#     requirements = f.readlines()

setuptools.setup(
    name="camtono-derivatives",  # Replace with your own username
    version="0.0.22",
    author="DOT",
    author_email="dot@adara.com",
    description="Simplified advertising integrations",
    long_description="",
    long_description_content_type="text/markdown",
    include_package_data=True,
    url="https://bitbucket.org/adarainc/camtono-derivatives-pkg",
    setup_requires=['pytest-runner'],
    packages=['camtono.derivatives'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "camtono-parser>=0.0.5"
    ]
)
