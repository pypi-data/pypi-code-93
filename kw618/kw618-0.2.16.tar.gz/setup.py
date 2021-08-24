"""
Setup for the kw618 package.

上传 pypi 的流程:
    1. 修改下面的 version 号
    2. python setup.py check   # 检查setup文件是否有误
    3. python setup.py sdist bdist_wheel # 编译必要文件并打包
    4. 在dist目录中, 删除旧版本的 kw618
    5. twine upload dist/*  # 将库包上传到pypi (需要使用到twine库)


"""

import setuptools

# 这里的依赖包只需要写"第三方库包"即可, 标准库的包不用写(写了反而报错!)
install_requires = [
    # requests相关
    "retry", "pysnooper", "user_agent", "requests",
    "scrapy", "uuid", "PyExecJS",
    "exchangelib", "urllib3", "selenium",
    # pandas相关
    "numpy", "pandas", "pymongo",
    # pymongo相关
    "pymongo", "redis",
    # pymysql相关
    "pymysql", "sqlalchemy",
    # 其他
    "schedule",
    # 加密相关
    "pycryptodome",
]

# 版本号: 每次上传前都需要更新
version = "0.2.16"

with open('README.md') as f:
    README = f.read()

setuptools.setup(
    author="Kerwin Lui",
    author_email="kerwin19950830@gmail.com",
    name='kw618',
    license="MIT",
    description='integrated commonly used third-party libraries to personal use',
    version=version,
    long_description=README,
    url='https://gitee.com/kerwin_van_lui/kw618',
    packages=setuptools.find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*", "*.tags*"]),
    python_requires=">=3.6",
    include_package_data=True,  # 
    install_requires=install_requires,
    classifiers=[
        # Trove classifiers
        # (https://pypi.python.org/pypi?%3Aaction=list_classifiers)
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
)
