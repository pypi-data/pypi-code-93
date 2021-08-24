import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="album_sender",
    version="0.0.54",
    author="Yunzhi Gao",
    author_email="gaoyunzhi@gmail.com",
    description="Telegram album sender.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gaoyunzhi/telegram_album_sender",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'cached_url',
        'telegram_util',
        'pic_cut',
    ],
    python_requires='>=3.0',
)