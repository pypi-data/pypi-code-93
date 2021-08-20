from setuptools import setup

def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="sms-boomber",
    version="1.4.9",
    description="",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/shehan9909/sms-boomber",
    author="shehan_slahiru",
    author_email="www.shehan6472@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["sms_boomber"],
    include_package_data=True,
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "sms-boomber=sms_boomber.__main__:main",
        ]
    },
)
