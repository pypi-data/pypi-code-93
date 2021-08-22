from setuptools import setup, find_packages

setup(
    name='Orf-callback',
    version="0.0.3",
    author="Brief",
    author_email='brf2053@gmail.com',
    description='For persional use.',
    long_description="For persional use",
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(),
    python_requires='>=3.5',
    install_requires=[
        "Orf-sendMsg",
        "requests"
    ]
)