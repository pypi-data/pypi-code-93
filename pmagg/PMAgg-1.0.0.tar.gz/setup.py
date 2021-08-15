import setuptools

if __name__ == '__main__':
    with open("README.md", "r", encoding='utf-8') as fh:
        long_description = fh.read()
    setuptools.setup(
        name="PMAgg",
        version="1.0.0",
        author="jcl",
        author_email="2195932461@qq.com",
        description="A matplotlib GUI backend with interactive capabilities",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://gitee.com/lvvl/pmagg",
        packages=setuptools.find_packages(),
        # package_dir={'PMAgg':'PMAgg'},
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.5',
        include_package_data=True,
        # entry_points={
        #     "console_scripts":[
        #         "PMAgg=PMAgg.PMAgg:main"
        #     ]
        # }
        install_requires=['PySide2', 'matplotlib'],
    )
