# coding=utf-8

try:
    from setuptools import setup, find_packages
    # res = find_packages()
except ImportError:
    from distutils.core import setup

setup(
    name='yuan-tool',  # 打包后的包文件名
    version='1.88',  # 版本号
    keywords="pip",  # 关键字
    description='some common components for personal use',  # 说明
    long_description="some common components for personal use",  # 详细说明
    # license="MIT Licence",  # 许可
    url='',  # 一般是GitHub项目路径
    author='narukami_yume',
    author_email='100961220@qq.com',
    # packages=find_packages(),     #这个参数是导入目录下的所有__init__.py包
    include_package_data=True,
    platforms="any",
    python_requires='>=3.6',
    install_requires=['requests>=2.25',
                      'lxml>=4.5.2',
                      'IPy>=1.01',
                      'PyYAML>=5.4.1',
                      'paramiko',
                      'colorama',
                      'pycryptodome',
                      'ruamel.yaml',
                      'redis',
                      'pymongo',
                      'pymysql',
                      'kafka-python',
                      'elasticsearch',
                      'DBUtils',
                      'pyDes',
                      'Crypto',
                      'dnspython',
                      'tld',
                      'psutil',
                      'cchardet'
                      ],  # 引用到的第三方库
    # py_modules=['pip-test.DoRequest', 'pip-test.GetParams', 'pip-test.ServiceRequest',
    #             'pip-test.ts.constants', 'pip-test.ac.Agent2C',
    #             'pip-test.ts.ttypes', 'pip-test.ac.constants',
    #             'pip-test.__init__'],  # 你要打包的文件，这里用下面这个参数代替
    packages=['yuantool', 'yuantool.database', 'yuantool.network']  # 这个参数是导入目录下的所有__init__.py包
)
