from setuptools import setup, find_packages
setup(
    name='uitestrunner_syberos',
    version='0.14',
    author='Jinzhe Wang',
    description='A ui automated testing tool for SyberOS',
    author_email='wangjinzhe@syberos.com',
    url='http://www.syberos.cn/',
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=["uitestrunner_syberos.Application",
                "uitestrunner_syberos.Device",
                "uitestrunner_syberos.Item",
                "uitestrunner_syberos.Connection",
                "uitestrunner_syberos.Events",
                "uitestrunner_syberos.setup",
                "uitestrunner_syberos.__main__"],
    package_data={
        "uitestrunner_syberos": ["data/com.syberos.sgt-1.0.2.sop"]
    }
)
