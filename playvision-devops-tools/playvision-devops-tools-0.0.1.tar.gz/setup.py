import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="playvision-devops-tools",
    version="0.0.1",
    author="Dmitriy Shelestovskiy",
    author_email="one@sonhador.ru",
    description="Playvision devops tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'backuper=playvision.main'
        ]
    },
    install_requires=[
        "python-keystoneclient==4.2.0",
        "python-swiftclient==3.12.0"
    ]
)
