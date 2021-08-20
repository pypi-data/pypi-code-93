from setuptools import setup, find_packages

setup(
    name="PyCheer",
    version="1.0.9",
    author="cyrxdzj",
    author_email="cyrxdzj@qq.com",
    url="https://gitee.com/cyrxdzj/PyCheer",
    long_description="Please see https://gitee.com/cyrxdzj/PyCheer",
    packages=[
        'PyCheer',
    ],
    package_dir={'PyCheer': 'PyCheer'},
    package_data={
        'PyCheer': ['html/*.html', 'js/*.js', 'js/theme/*.js', 'js/mode/*.js', 'css/*.css', 'logo/*']
    },
    license="MulanPSL-2.0",
    zip_safe=False,
    keywords='PyCheer',
    entry_points={
        'console_scripts': [
            'pycheer=PyCheer:main_function',
            'PyCheer=PyCheer:main_function'
        ]
    },
    install_requires=[
        "flask",
        "GitPython"
    ]
)
