from setuptools import setup, find_packages, find_namespace_packages

setup(
    name='Orf-sendMsg',
    version="0.0.4",
    author="Brief",
    author_email='brf2053@gmail.com',
    description='For persional use.',
    long_description="For persional use",
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=find_namespace_packages(
        include=["Orf_sendMsg", "Orf_sendMsg.*", ]
    ),
    python_requires='>=3.5',
    install_requires=[
        "requests"
    ],
    include_package_data=True
)