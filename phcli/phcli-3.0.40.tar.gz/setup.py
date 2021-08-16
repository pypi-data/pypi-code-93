import io
import setuptools
from glob import glob
from phcli.define_value import CLI_CLIENT_VERSION


with io.open("./README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="phcli",
    version=CLI_CLIENT_VERSION,
    author="Alfred Yang",
    author_email="alfredyang@pharbers.com",
    maintainer="ClockQ,AlexQian,hbzhao",
    maintainer_email="zyqi@pharbers.com,pqian@pharbers.com,15847059648@163.com",
    description="pharbers dag scheduler config",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
    install_requires=[
        "requests",
        "click",
        "boto3",
        "pyyaml",
        "pandas",
        "xlrd",
        "pypinyin",
        "psycopg2",
        "sqlalchemy",
        "pymysql",
    ],
    package_data={
        '': ['template/*.yaml', 'template/*.tmp'],
    },
    data_files=[
        ('', glob('file/ph_data_clean/mapping_table/*')),
    ],
    entry_points={
        'console_scripts': [
            'phcli = phcli.__main__:phcli',
        ],
    }
)
