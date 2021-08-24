from setuptools import setup, find_packages


LONGDOC=''' fly_log
========

最简单的日志，比 print 函数，多了时间与源文件信息。用于比较小的python项目，是适合的。


'''

setup(
    name = 'fly_log',
    version = '0.1.20',
    keywords='fly log debug',
    description = 'a simple log for small project',
    long_description=LONGDOC,
    license = 'MIT License',
    url = 'https://github.com/zero-space-man-community/fly_log',
    author = 'flythinker',
    author_email = 'flythinker@qq.com',
    # packages = find_packages(),
    packages=['fly_log'],
    package_dir={'fly_log':'fly_log'},
    include_package_data = True,
    platforms = 'any',
    install_requires = [],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
      ],
)