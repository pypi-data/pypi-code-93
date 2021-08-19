import setuptools

setuptools.setup(
    name="work_wechat_sdk",
    version="1.0",
    description="for work wechat API",
    long_description="work_wechat Module",
    long_description_content_type='text/markdown',
    python_requires=">=3.5.0",
    license="MIT Licence",

    author="zouxingshun",
    author_email="1424798946@qq.com",
    url="https://gitee.com/zouxingshun/work_wechat_sdk",

    packages=setuptools.find_packages(),
    keywords='workwechat',
    include_package_data=True,
    platforms="any",
    install_requires=["requests"],
)
