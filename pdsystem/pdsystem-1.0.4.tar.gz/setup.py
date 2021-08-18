from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
setup(
    name='pdsystem',
    py_modules=['pdsystem'],
    version='1.0.4',
    description='判断系统',
    long_description=long_description,
    long_description_content_type="text/markdown", 
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.6',
    install_requires=['colorama'],    # install_requires字段可以列出依赖的包信息，用户使用pip或easy_install安装时会自动下载依赖的包
    author='神秘人',
    url='https://pypi.org/project/ycc',
    author_email='3046479366@qq.com',
    license='MIT',
    packages=find_packages(),   # 需要处理哪里packages，当然也可以手动填，例如['pip_setup', 'pip_setup.ext']
    include_package_data=False,
    zip_safe=False,
)