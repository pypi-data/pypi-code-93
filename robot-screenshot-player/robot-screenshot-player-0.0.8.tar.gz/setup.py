import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="robot-screenshot-player",
    version="0.0.8",
    author="pradeep kumar",
    author_email="pradeepkmr838@gmail.com",
    description="utility for playing all the screentshot captured during robot execution",
    long_description="utility for playing all the screentshot captured during robot execution",
    long_description_content_type="text/markdown",
    url="https://github.com/Pradeepkumar1qa/Robot-Screenshot-Player",
    project_urls={
        "Bug Tracker": "https://github.com/Pradeepkumar1qa/Robot-Screenshot-Player/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=['robot-framework','video-player','automation','screenshot-player'],
    package_dir={"": "robotscreenshotplayer"},
    py_modules=['ScreenShotPlayer'],
    packages=setuptools.find_packages(where="robotscreenshotplayer"),
    python_requires=">=3.6",
    package_data={'': ['*.css','*.js']}
)