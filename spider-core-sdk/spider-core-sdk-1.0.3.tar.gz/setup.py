from setuptools import setup


setup(
    name='spider-core-sdk',
    version='1.0.3',
    author='wog',
    description='',
    packages=['spider_core'],
    python_requires='>=3.7',
    install_requires=['requests>=2.25.0', 'scrapy>=2.5.0'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
)
