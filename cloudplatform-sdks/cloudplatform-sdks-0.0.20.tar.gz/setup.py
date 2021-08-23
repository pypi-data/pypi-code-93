from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(name='cloudplatform-sdks',  # 包名
      version='0.0.20',  # 版本号
      description='SDK for platforms',
      long_description=long_description,
      author='cloudchef',
      author_email='yuhui.yan@cloudchef.io',
      url='https://github.com/',
      install_requires=[
          "tencentcloud-sdk-python==3.0.423",
          "aliyun-python-sdk-core==2.13.35",
          "aliyun-python-sdk-cdn==3.6.4",
          "aliyun-python-sdk-nas==3.11.0",
          "aliyun-python-sdk-dds==3.5.4",
          "proxy-tools==0.1.0",
          "huaweicloudsdkcore==3.0.49",
          "huaweicloudsdkecs==3.0.49",
          "huaweicloudsdkeip==3.0.49",
          "huaweicloudsdkevs==3.0.49",
          "huaweicloudsdkiam==3.0.49",
          "huaweicloudsdkims==3.0.49",
          "huaweicloudsdkvpc==3.0.49",
          "huaweicloudsdkbss==3.0.51"
      ],
      license='Apache License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
      ],
)
