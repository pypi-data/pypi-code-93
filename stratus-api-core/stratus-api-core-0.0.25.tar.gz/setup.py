import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()
# with open('requirements.txt') as f:
#     requirements = f.readlines()
setuptools.setup(
    name="stratus-api-core",  # Replace with your own username
    version="0.0.25",
    author="adara",
    author_email="dot@adara.com",
    description="An API stratus_api for simplified development",
    long_description="",
    long_description_content_type="text/markdown",
    include_package_data=True,
    setup_requires=['pytest-runner'],
    url="https://bitbucket.org/adarainc/framework-base",
    packages=['stratus_api.core'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "connexion[swagger-ui]==2.6.0",
        "gunicorn>=20.0.4",
        "requests[security]>=2.7.0",
        "pytest>=5.4.1",
        "pytest-cov>=2.8.1",
        "responses>=0.10.14",
        "tenacity>=6.1.0",
        "flake8>=3.7.9",
        "aiohttp>=3.6.2",
        "uvicorn>=0.11.3",
        "aiohttp_jinja2>=1.2.0",
        "pytest-aiohttp",
        "uvloop"
    ]
)
