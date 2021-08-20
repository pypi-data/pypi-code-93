from setuptools import setup, find_packages

setup(
    name="gecko-common",
    version="0.1.8",
    author="sgy",
    author_email="ericsgy@163.com",
    description="gecko common library",
    url="https://gitlab.com/winwin2021/common",
    license='MIT',
    keywords='binance huobi ok exchange',

    # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    packages=find_packages(exclude=('tests',)),

    # 分类信息
    classifiers=[
        # 发展时期
        'Development Status :: 3 - Alpha',
        # 开发的目标用户
        'Intended Audience :: Developers',
        # 类型
        'Topic :: Software Development :: Libraries :: Python Modules',
        # 许可证信息
        'License :: OSI Approved :: MIT License',
        # 目标 Python 版本
        'Programming Language :: Python :: 3.7'
    ],

    # 表明当前模块依赖哪些包，若环境中没有，则会从pypi中下载安装
    install_requires=[
        'aiohttp >= 3.6.2, <=4',
        'python-binance2',
    ],
    # 仅在测试时需要使用的依赖，在正常发布的代码中是没有用的
    # 在执行python setup.py test时，可以自动这些库，确保测试的正常运行
    test_requires=[
        'requests >=2.25.1, <=3',
        'requests-mock >=1.9.2, <=2',
        'pytest >=6.2.4, <=7',
        'pytest-asyncio >= 0.15.1'
    ],

    python_requires='>=3.7',
)
