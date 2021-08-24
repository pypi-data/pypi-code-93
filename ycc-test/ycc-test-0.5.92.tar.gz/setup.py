from setuptools import setup, find_packages
import os
__author__ = '神秘的·'
__project_start_time__='2020'
__date_end_time__ = '2021/7,2021/8'
HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, "README.rst")) as fid:
    R= fid.read()
setup(
    name='ycc-test', # 名称 #test
    py_modules=['core','__init__','run'],
    version='0.5.92',#sycc0.5.7#ycc-test0.5.8
    description='三圆计算器,cmd或shell(Terminal) sycc命令开始运行,ps:ycc是原版,sycc是因作者需要而定制版(不推荐下载) ycc-tset版本是ycc和sycc测试上传版本(请勿下载)', # 
    long_description = R,
   # long_description_content_type='text/markdown',
    classifiers=[
    'Natural Language :: Chinese (Simplified)',
    'Development Status :: 6 - Mature',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Android',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Topic :: Terminals',
    'Topic :: System :: Shells',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Intended Audience :: Developers',],  #new
    keywords=['ycc','3y','a_3y','Circle','圆','圆柱','圆环','py','Chinese','sycc',
    'python','windows','linux','3','y','yc','yz'],# 关键字 #test
    author=__author__, # 作者
    author_email='3046479366@qq.com', 
    url='http://pypi.org/project/ycc', # 包含包的项目地址
    license='MIT', # 授权方式
    packages=["p","k","e"],#未修改#"p","k","e",
    python_requires='>=3.6',
    platfrom=['any'],
    install_requires=['pdsystem>=1.0.4'],
    entry_points = {
        'console_scripts': [
            'sycc = run:main',
        ]
    },
    project_urls = {
    'pydroid(python for android仅限中国大陆使用': 'https://wws.lanzoui.com/iK2GFm24t3a',
    'pydroid文件密码python' : 'https://wws.lanzoux.com/iK2GFm24t3a'
    },
    include_package_data=True,
    zip_safe=False,
)