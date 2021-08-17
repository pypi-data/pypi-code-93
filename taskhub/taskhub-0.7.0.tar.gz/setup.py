from setuptools import setup, find_packages

setup(
    name='taskhub',
    version="0.7.0",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
    },
    install_requires=[
        "retry",
        "loger>=1.0",
    ],
    url='https://github.com/iridesc/taskhub',
    license='GNU General Public License v3.0',
    author='Irid Zhang',
    author_email='irid.zzy@gmail.com',
    description='一个任务分发与结果收集中间件'
)
