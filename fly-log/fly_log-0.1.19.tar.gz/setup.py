from setuptools import setup, find_packages

setup(
    name = 'fly_log',
    version = '0.1.19',
    keywords='fly log debug',
    description = 'a simple log for small project',
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